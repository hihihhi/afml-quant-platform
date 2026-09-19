#pragma once

#include <string_view>

namespace afml {

// This reports build scope only. It is not a strategy or market-data interface.
// Real components require approved book-derived contracts before implementation.
struct BuildStatus {
    std::string_view stage;
    bool market_data_ready;
    bool backtesting_ready;
    bool live_trading_enabled;
};

[[nodiscard]] BuildStatus build_status() noexcept;
[[nodiscard]] std::string_view status_json() noexcept;

} // namespace afml
