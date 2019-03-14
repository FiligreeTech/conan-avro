from conans import ConanFile, CMake, tools


class AvroConan(ConanFile):
    name = "avro"
    version = "1.8.2"
    license = "Apache-2.0"
    url = "https://avro.apache.org/"
    description = "https://avro.apache.org/"
    topics = ("avro")
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [False], "fPIC":[True]}
    default_options = "shared=False", "fPIC=True"
    generators = "cmake"
    requires = "boost/1.68.0@conan/stable"

    def source(self):
        self.run("git clone git://github.com/FiligreeTech/avro.git")
        self.run("cd avro && git checkout BytesTwoPassDecoderWIP")
        # This small hack might be useful to guarantee proper /MT /MD linkage
        # in MSVC if the packaged project doesn't have variables to set it
        # properly

        tools.replace_in_file("avro/lang/c++/CMakeLists.txt", 'project (Avro-cpp)',
                              '''project (Avro-cpp)
include(${CMAKE_BINARY_DIR}/conanbuildinfo.cmake)
conan_basic_setup()''')

        #Remove the unittests which require other dependencies
        def replaceText(l, sub=""):
            tools.replace_in_file("avro/lang/c++/CMakeLists.txt", l, sub)

        #Remove the unittests which require other dependencies
        replaceText("""unittest (buffertest)
unittest (unittest)
unittest (SchemaTests)
unittest (LargeSchemaTests)
unittest (CodecTests)
unittest (StreamTests)
unittest (SpecificTests)
unittest (DataFileTests)
unittest (JsonTests)
unittest (AvrogencppTests)
unittest (CompilerTests)

add_dependencies (AvrogencppTests bigrecord_hh bigrecord_r_hh bigrecord2_hh
    tweet_hh
    union_array_union_hh union_map_union_hh union_conflict_hh
    recursive_hh reuse_hh circulardep_hh empty_record_hh)
""")

        #For now remove avrogen and precompile - issues with linking
        replaceText("add_executable (avrogencpp impl/avrogencpp.cc)")
        replaceText("target_link_libraries (avrogencpp avrocpp_s ${Boost_LIBRARIES})")
        replaceText("install (TARGETS avrogencpp RUNTIME DESTINATION bin)")
        replaceText("add_executable (precompile test/precompile.cc)")
        replaceText("target_link_libraries (precompile avrocpp_s ${Boost_LIBRARIES})")


    def configure_cmake(self):
        cmake = CMake(self)
        cmake.vebose = True
        cmake.configure(source_folder="avro/lang/c++")
        return cmake

    def build(self):
        self.configure_cmake().build()

    def package(self):
        self.configure_cmake().install()

    def package_info(self):
        self.cpp_info.libs = ["avrocpp_s"]


