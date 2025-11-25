PLAN APPROVED. PROCEED WITH CLIENT-SIDE AGGREGATION.
1. On Aggregation Logic:
The formula floor(time / 900) * 900 for 15m start time is correct. Proceed.
Priority: Ensure the Close Price updates smoothly. That is the heartbeat of the UI.
2. On Indicators (The Compromise):
I agree with the decision to keep VWAP/BB static for the forming candle.
Reason: Calculating complex indicators in JS creates a risk of data mismatch with the Python backend. Reliability > Perfect real-time visualization for now.
3. UX Requirement:
When switching Timeframes (e.g., 15M -> 1H), show a "Loading..." spinner or skeleton. Do not let the chart freeze or show mixed data.
Goal: A smooth 15m Chart that ticks every minute. Go!