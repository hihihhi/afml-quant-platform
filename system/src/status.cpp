#include "afml/status.hpp"

namespace afml {

BuildStatus build_status() noexcept {
    return {
        .stage = "bootstrap_only",
        .market_data_ready = false,
        .backtesting_ready = false,
        .live_trading_enabled = false,
    };
}

std::string_view status_json() noexcept {
    // A fixed literal avoids implying that unimplemented capability discovery
    // or a live connection exists. Tests keep it consistent with BuildStatus.
    return R"({"stage":"bootstrap_only","market_data_ready":false,"backtesting_ready":false,"live_trading_enabled":false})";
}

} // namespace afml
