#include <torrent/object.h>

#include <iostream>

int main() {
    int passed = 0;

    torrent::Object value(42);
    if (value.is_value() && value.as_value() == 42) {
        ++passed;
    }

    torrent::Object string("openharmony");
    if (string.is_string() && string.as_string() == "openharmony") {
        ++passed;
    }

    torrent::Object map = torrent::Object::create_map();
    map.insert_key("answer", torrent::Object(42));
    if (map.is_map() && map.get_key_value("answer") == 42) {
        ++passed;
    }

    std::cout << "libtorrent functional checks passed: " << passed << "/3\n";
    return passed == 3 ? 0 : 1;
}

