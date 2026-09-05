#include <boost/filesystem.hpp>

#include <cassert>
#include <fstream>
#include <iostream>

int main() {
    namespace fs = boost::filesystem;
    const fs::path directory = "boost-filesystem-consumer";
    const fs::path file = directory / "payload.txt";
    fs::remove_all(directory);
    assert(fs::create_directory(directory));
    std::ofstream(file.string()) << "OpenHarmony";
    assert(fs::exists(file));
    assert(fs::file_size(file) == 11);
    std::size_t entries = 0;
    for (fs::directory_iterator it(directory), end; it != end; ++it)
        ++entries;
    assert(entries == 1);
    fs::remove_all(directory);
    std::cout << "boost filesystem consumer test passed" << std::endl;
    return 0;
}
