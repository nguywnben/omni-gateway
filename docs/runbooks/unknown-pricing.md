# Unknown model pricing

1. Identify the requested model and virtual key pricing policy from **Access** and request traces.
2. Add a reviewed price to `model_pricing.json`, select an explicit bounded fallback price, or keep
   the default deny policy. Do not silently allow unpriced hard-budget traffic.
3. Exercise a small request and verify estimated and actual cost settlement.
4. Confirm the `pricing_denied` or `pricing_warned` counter stops increasing.
