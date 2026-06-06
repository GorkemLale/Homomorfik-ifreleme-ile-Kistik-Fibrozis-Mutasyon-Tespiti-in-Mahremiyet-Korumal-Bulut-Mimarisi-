#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <seal/seal.h>
#include <vector>
#include <sstream>
#include <string>
#include <memory>

namespace py = pybind11;
using namespace seal;
using namespace std;

const size_t POLY_MODULUS_DEGREE = 8192;
const int PLAIN_MODULUS_BIT_SIZE = 20;

// Helper function to serialize SEAL objects to bytes
template <class T>
py::bytes save_to_bytes(const T &obj) {
    std::stringstream stream;
    obj.save(stream);
    return py::bytes(stream.str());
}

// Helper function to serialize params
py::bytes save_parms_to_bytes(const EncryptionParameters &parms) {
    std::stringstream stream;
    parms.save(stream);
    return py::bytes(stream.str());
}

// Helper to create parameters
EncryptionParameters create_parms() {
    EncryptionParameters parms(scheme_type::bfv);
    parms.set_poly_modulus_degree(POLY_MODULUS_DEGREE);
    parms.set_coeff_modulus(CoeffModulus::BFVDefault(POLY_MODULUS_DEGREE));
    parms.set_plain_modulus(PlainModulus::Batching(POLY_MODULUS_DEGREE, PLAIN_MODULUS_BIT_SIZE));
    return parms;
}

class SEALEngineCpp {
private:
    EncryptionParameters parms_;
    SEALContext context_;
    PublicKey public_key_;
    SecretKey secret_key_;
    std::unique_ptr<Encryptor> encryptor_;
    std::unique_ptr<Decryptor> decryptor_;
    std::unique_ptr<BatchEncoder> encoder_;
    std::unique_ptr<Evaluator> evaluator_;

public:
    SEALEngineCpp() 
        : parms_(create_parms()),
          context_(parms_)
    {
        KeyGenerator keygen(context_);
        keygen.create_public_key(public_key_);
        secret_key_ = keygen.secret_key();
        
        encryptor_ = std::make_unique<Encryptor>(context_, public_key_);
        decryptor_ = std::make_unique<Decryptor>(context_, secret_key_);
        encoder_ = std::make_unique<BatchEncoder>(context_);
        evaluator_ = std::make_unique<Evaluator>(context_);
    }

    size_t get_slot_count() const {
        return encoder_->slot_count();
    }

    py::bytes encrypt_vector(const std::vector<uint64_t> &int_vector) {
        Plaintext plaintext;
        encoder_->encode(int_vector, plaintext);
        Ciphertext ciphertext;
        encryptor_->encrypt(plaintext, ciphertext);
        return save_to_bytes(ciphertext);
    }

    std::vector<uint64_t> decrypt_vector(const std::string &cipher_bytes) {
        Ciphertext ciphertext;
        std::stringstream stream(cipher_bytes);
        ciphertext.load(context_, stream);
        
        Plaintext plaintext;
        decryptor_->decrypt(ciphertext, plaintext);
        
        std::vector<uint64_t> result;
        encoder_->decode(plaintext, result);
        return result;
    }

    py::dict get_public_context_bytes() {
        py::dict result;
        result["parms"] = save_parms_to_bytes(parms_);
        return result;
    }
};

EncryptionParameters load_parms(const std::string &parms_bytes) {
    EncryptionParameters parms(scheme_type::bfv);
    std::stringstream stream(parms_bytes);
    parms.load(stream);
    return parms;
}

class SEALEvaluatorCpp {
private:
    SEALContext context_;
    std::unique_ptr<Evaluator> evaluator_;

public:
    SEALEvaluatorCpp(const std::string &parms_bytes) 
        : context_(load_parms(parms_bytes))
    {
        evaluator_ = std::make_unique<Evaluator>(context_);
    }

    py::bytes compute_difference(const std::string &cipher1_bytes, const std::string &cipher2_bytes) {
        Ciphertext ct1, ct2;
        std::stringstream stream1(cipher1_bytes);
        std::stringstream stream2(cipher2_bytes);
        
        ct1.load(context_, stream1);
        ct2.load(context_, stream2);

        Ciphertext diff;
        evaluator_->sub(ct1, ct2, diff);

        return save_to_bytes(diff);
    }
};

PYBIND11_MODULE(seal_cpp, m) {
    m.doc() = "Microsoft SEAL direct C++ bindings for DNA Mutation Analysis";

    py::class_<SEALEngineCpp>(m, "SEALEngineCpp")
        .def(py::init<>())
        .def("get_slot_count", &SEALEngineCpp::get_slot_count)
        .def("encrypt_vector", &SEALEngineCpp::encrypt_vector)
        .def("decrypt_vector", &SEALEngineCpp::decrypt_vector)
        .def("get_public_context_bytes", &SEALEngineCpp::get_public_context_bytes);

    py::class_<SEALEvaluatorCpp>(m, "SEALEvaluatorCpp")
        .def(py::init<const std::string &>())
        .def("compute_difference", &SEALEvaluatorCpp::compute_difference);
}
