#define BOOST_TEST_MODULE boost_unit_test_framework_consumer

#include <boost/test/unit_test.hpp>
#include <string>

BOOST_AUTO_TEST_CASE(string_and_arithmetic_assertions) {
    const std::string value = "OpenHarmony";
    BOOST_TEST(value == "OpenHarmony");
    BOOST_TEST(value.size() == 11U);
    BOOST_TEST(2 + 3 == 5);
}
