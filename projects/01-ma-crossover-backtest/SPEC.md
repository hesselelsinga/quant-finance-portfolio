# Project 01: Moving-average crossover backtest (done honestly)

## The question
Does the classic 50/200-day moving-average crossover beat buy-and-hold on the S&P 500 once you
include transaction costs and avoid look-ahead bias?

The point isn't to find a winning strategy. It's to build a **correct, reusable backtesting
foundation** and show that I know how backtests mislead. Every later project uses this code.

## Setup
- Asset: SPY (S&P 500 ETF), daily, adjusted close, 2005-01-01 to today, from yfinance.
- Strategy (long-only): hold SPY when SMA50 > SMA200, otherwise hold cash (cash return = 0 to start).
- Benchmark: buy-and-hold SPY over the same period.
- Transaction cost: charged per unit of turnover, `cost = cost_bps / 10_000 * |position_t - position_{t-1}|`.
  Default 10 bps.

## Milestones
**M0: Environment.** Create the venv, `requirements.txt` and `.gitignore`, run `git init`, create the
GitHub repo, and make the first commit. (Claude may write the boilerplate.)

**M1: Data.** Write a function that downloads SPY, caches it to `data/`, and returns a clean price
series. Check for missing values and plot the price to make sure it looks right.

**M2: Signal.** Compute SMA50 and SMA200 and a 0/1 signal. Decide how to handle the first 200 days.

**M3: Backtest engine.** Turn the signal into a position, **lagged by one day** (decide on day t,
earn the return on day t+1). Compute strategy returns, subtract costs, and build the equity curve.
Write it as a general `run_backtest(prices, signal, cost_bps)` function that I can reuse with any
signal later.

**M4: Metrics (put these in `common/`, they're reused later).** For the strategy and the benchmark:
- CAGR
- annualized volatility
- Sharpe ratio (risk-free = 0 for now; state that assumption)
- maximum drawdown and its dates
- number of trades
- % of time in the market

**M5: The honesty experiments.** This is the core of the write-up.
1. **Look-ahead:** run the backtest once *without* the one-day lag. How much better does it look?
   Explain why that result is fake.
2. **Costs:** a results table at 0, 5, 10 and 25 bps.
3. **Benchmark:** strategy against buy-and-hold on return, volatility, Sharpe and drawdown. Where
   does the strategy actually help? (Hint: look at drawdowns in 2008 and 2020.)

**M6: Charts (saved to `figures/`).**
- Equity curves for the strategy and buy-and-hold, on a log scale.
- Drawdown curves for both.

**M7: Tests (pytest).** At least these four:
- **No look-ahead:** changing prices *after* day t must not change the position on day t.
- **Sanity:** an always-long signal at 0 cost must reproduce buy-and-hold.
- **Costs:** higher costs can never increase the final equity.
- **Known answer:** max drawdown on a small hand-made price series equals the value I worked out by hand.

**M8: README and LinkedIn.** Write the results README (see the conventions in `CLAUDE.md`), push to
GitHub, and draft the LinkedIn post.

## Stretch goals (optional)
- A cash return from the 3-month T-bill (FRED, series `DTB3`) instead of 0.
- A parameter grid (for example short window 20-100, long window 100-300) shown as a Sharpe
  heatmap, with a written warning about overfitting and multiple testing. Then pick parameters on
  2005-2015 and test them only on 2016 to today.
- Run the same strategy on other assets (AEX index, gold, bonds) and compare.

## Definition of done
- The code runs from a fresh clone with one command.
- All tests pass.
- The README has the results table, both charts, and one clear lesson.
- I can answer without notes: why lag the signal? Why does the crossover cut drawdowns but often
  lose on return? What would make this result statistically meaningless?
