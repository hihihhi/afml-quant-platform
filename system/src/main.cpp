#include "afml/status.hpp"

#include <iostream>
#include <string_view>

int main(int argc, char* argv[]) {
    if (argc == 2 && std::string_view(argv[1]) == "--status") {
        std::cout << afml::status_json() << '\n';
        return 0;
    }

    std::cerr << "Usage: afml-platform --status\n"
              << "Only the C++ build scaffold exists. Market data, backtesting, "
                 "models and live trading are not implemented or enabled.\n";
    return 2;
}
