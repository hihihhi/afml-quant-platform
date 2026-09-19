#include "afml/status.hpp"

#include <iostream>
#include <string_view>

int main() {
    const auto status = afml::build_status();
    if (status.stage != "bootstrap_only" || status.market_data_ready || status.backtesting_ready ||
        status.live_trading_enabled) {
        std::cerr << "The bootstrap build must not advertise unfinished capabilities.\n";
        return 1;
    }

    constexpr std::string_view expected =
        R"({"stage":"bootstrap_only","market_data_ready":false,"backtesting_ready":false,"live_trading_enabled":false})";
    if (afml::status_json() != expected) {
        std::cerr << "CLI status does not match the tested build contract.\n";
        return 1;
    }
    return 0;
}
