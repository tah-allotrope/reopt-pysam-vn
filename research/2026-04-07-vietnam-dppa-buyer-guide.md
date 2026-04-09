# Vietnam DPPA buyer guide

Plain-English answer to: as a large energy buyer in Vietnam's synthetic/financial DPPA, what am I really paying per kWh?

## Bottom line

- For each kWh that is covered by the DPPA in a trading interval, your all-in cost is **roughly**:

```text
all-in matched kWh ~= strike price + DPPA charge + small basis/loss adjustment
```

- In the 2025 example materials reviewed here, that is approximately:

```text
2,100 + 523.34 + small adjustment ~= 2,623 to 2,670 VND/kWh
```

- The reason is simple:
  - you still pay EVN/EVN PC for the electricity taken from the grid at a market-linked price;
  - you also pay the generator or receive from the generator the **difference** between the strike price and the market price under the CfD;
  - those two market-price pieces mostly cancel each other out;
  - what remains is basically the **strike price**, plus the **regulated DPPA system charges**, plus a small loss/basis effect.

- For any kWh of your load **not** covered by DPPA generation in that interval, you pay the normal EVN retail tariff for the shortfall.

- If your contract settles on more generation than you actually consume in an interval, you may also pay CfD on that excess contracted volume. That can push your effective consumed-kWh cost materially higher.

## The terms in simple English

### 1) Strike price / contract price

This is the negotiated fixed price in your forward contract (CfD) with the renewable generator.

- Think of it as your target renewable price.
- Example in the slides: **2,100 VND/kWh**.

### 2) Market price / spot price / FMP

This is the wholesale market reference price used in settlement.

- The reviewed documents define **FMP = SMP + CAN**.
- In plain English: energy market price plus market capacity price.
- Example in the slides: **1,700 VND/kWh**.

### 3) CfD settlement

This is the financial true-up between you and the generator.

```text
CfD payment = contracted quantity x (strike price - FMP)
```

- If strike price is **above** FMP, you pay the generator.
- If strike price is **below** FMP, the generator pays you.

### 4) CFMP

This is the market-linked price you pay to EVN PC for the DPPA-covered electricity volume.

- It is related to wholesale market pricing.
- In the example deck it is shown at **1,700 VND/kWh on average**.
- In practice, it is very close in spirit to the market reference price, but not always identical in every formula presentation.

### 5) DPPA charge / CDPPAdv / CCL

These are regulated add-on charges for using the system under the DPPA mechanism.

- One source shows:
  - **CDPPAdv = 360.14 VND/kWh**
  - **CCL = 163.2 VND/kWh**
- The example materials then combine them into a practical 2025 adder of:

```text
Total DPPA charge = 523.34 VND/kWh
```

Important nuance:

- Some materials show **CCL** as a separate invoice component.
- The worked examples effectively bundle it into one total DPPA adder.
- For a buyer trying to estimate total cost, using **523.34 VND/kWh** as the 2025 combined adder is the clearest shortcut from the reviewed documents.

### 6) KPP / loss coefficient

This is a multiplier applied to the market-linked EVN charge.

- Example in the slides: **1.027263**.
- This is why your exact all-in number is usually a bit higher than just `strike + DPPA charge`.

### 7) Retail tariff / CBL

This is what you pay for the part of your load that is **not** matched by DPPA generation in that interval.

- If your factory consumes more than the renewable plant produces in that interval, the shortfall is billed at EVN retail tariff.

## The buyer payment stack

For a single trading interval, a practical buyer view is:

```text
Total buyer payment
= payment to EVN PC
+ CfD payment to/from generator
```

### Payment to EVN PC

For the DPPA-covered volume, the reviewed materials indicate a structure like:

```text
matched volume x CFMP x KPP
+ matched volume x DPPA charge
```

For any shortfall volume, add:

```text
shortfall volume x retail tariff
```

### Payment under the CfD

```text
contracted quantity x (strike price - FMP)
```

## The simple all-in formula you can actually use

If your contracted quantity is roughly aligned with your matched consumption, then for each matched kWh:

```text
all-in matched kWh
~= (CFMP x KPP + DPPA charge) + (strike - FMP)
```

If CFMP is close to FMP, this simplifies to:

```text
all-in matched kWh ~= strike + DPPA charge + small basis/loss adjustment
```

And if you want a very fast mental shortcut:

```text
all-in matched kWh ~= strike + 523.34 VND/kWh    [using the 2025 example adder]
```

That shortcut ignores the loss/basis effect, so it is directionally useful, not exact.

## Worked example from the reviewed slides

### Assumptions taken from the example deck

- Load: **5,000 kWh** in the hour
- Strike price: **2,100 VND/kWh**
- FMP / CFMP assumption: **1,700 VND/kWh**
- KPP: **1.027263**
- Combined DPPA charge: **523.34 VND/kWh**

This gives an exact matched-kWh cost of:

```text
(1,700 x 1.027263) + 523.34 + (2,100 - 1,700)
= 1,746.3471 + 523.34 + 400
= 2,669.6871 VND/kWh
```

The quick shortcut version is:

```text
2,100 + 523.34 = 2,623.34 VND/kWh
```

So the shortcut understates the worked example by about **46.35 VND/kWh**, which comes from the loss/basis effect.

### Case A: solar covers part of your load

Assume the renewable plant covers **2,000 kWh** and your remaining **3,000 kWh** comes from normal EVN retail supply.

Using the example retail tariff of **1,833 VND/kWh** for the shortfall:

```text
EVN payment on shortfall
= 3,000 x 1,833
= 5,499,000 VND

EVN payment on DPPA-covered volume
= 2,000 x (1,700 x 1.027263)
+ 2,000 x 523.34
= 3,492,694.2 + 1,046,680
= 4,539,374.2 VND

CfD payment
= 2,000 x (2,100 - 1,700)
= 800,000 VND

Total buyer cost
= 5,499,000 + 4,539,374.2 + 800,000
= 10,838,374.2 VND
```

Effective average cost across the full 5,000 kWh load:

```text
10,838,374.2 / 5,000 = 2,167.67 VND/kWh
```

What this means:

- the **matched 2,000 kWh** effectively costs about **2,669.69 VND/kWh**;
- the **unmatched 3,000 kWh** still costs the normal retail tariff;
- your blended hourly average depends on how much of your load is actually matched by renewable output.

### Case B: solar generation exceeds your load

The slide deck also shows a case where load is **5,000 kWh** but solar generation is **7,500 kWh**, so there is **2,500 kWh excess generation** in the interval.

The example settles the CfD on the full **7,500 kWh** quantity:

```text
EVN payment
= 5,000 x (1,700 x 1.027263)
+ 5,000 x 523.34
= 11,348,435.5 VND

CfD payment
= 7,500 x (2,100 - 1,700)
= 3,000,000 VND

Total buyer cost
= 14,348,435.5 VND
```

Effective cost across the consumed 5,000 kWh:

```text
14,348,435.5 / 5,000 = 2,869.69 VND/kWh
```

Buyer takeaway:

- if the contract quantity can exceed your actual consumption in an interval, your effective consumed-kWh cost can jump;
- this is not just a price issue, it is also a **contract-shaping and settlement-volume** issue.

## The practical answer for an energy buyer

If you want one sentence:

```text
Your DPPA-covered kWh is not paid at just the strike price; in practice it is roughly strike price plus the regulated DPPA adder, and then adjusted a bit by market/loss mechanics.
```

Using the reviewed 2025 example inputs:

- **Fast estimate for matched DPPA kWh:** about **2,623 VND/kWh**
- **More exact worked-example matched DPPA kWh:** about **2,670 VND/kWh**
- **Unmatched kWh:** normal EVN retail tariff
- **Risk to watch:** paying CfD on excess contracted generation can push your effective consumed-kWh cost above that matched-kWh number

## What should you negotiate or verify before signing?

As a buyer, the biggest commercial questions are:

1. **What is the settlement quantity?**
   - Is CfD settled on generated volume, allocated volume, consumed volume, or the minimum of those?

2. **Is excess generation settled against you?**
   - This is the main driver of the bad midday-overgeneration outcome.

3. **What exactly is included in the DPPA adder?**
   - Ask whether invoices present CDPPAdv and CCL separately or as one combined adder.

4. **What loss coefficient applies to your connection voltage?**
   - This affects the exact all-in price.

5. **What retail tariff applies to shortfall energy by time period?**
   - Your overall savings depend heavily on the retail tariff avoided in each interval.

## Source notes

Documents reviewed:

- `background/Ecoplexus_ DPPA Presentation_Fof CEBA Workshop.pdf`
- `background/Simplified DPPA CfD Settlement Scenario .pptx`
- `background/synthetic DPPA Vietnam policy and regulation.pdf`

Key points cross-checked from the extracted text:

- generator market payment uses **FMP = SMP + CAN**;
- CfD is settled on **contract quantity x (strike price - market price)**;
- buyer EVN payments include market-linked energy charges, DPPA charges, and retail tariff for shortfall;
- one source separates **CCL**, while the simplified example combines it into the 2025 total DPPA adder of **523.34 VND/kWh**.

## Final takeaway

If you are the buyer, the cleanest mental model is:

```text
matched renewable kWh ~= strike price + regulated DPPA adder
shortfall kWh = normal EVN retail power
bad outcome risk = paying CfD on excess contracted generation
```

That is the simplest way to cut through the DPPA terminology without losing the commercial reality.
