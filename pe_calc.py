def calculate_intrinsic_value(roc_pre_tax, coc, initial_egv, growth_year, fade_period, terminal_growth, scrap):
    roc_pre_tax = roc_pre_tax / 100  # RoCE
    coc = coc / 100  # Cost of Capital
    initial_egv = initial_egv / 100  # Initial earnings growth rate
    growth_year = growth_year  # Initial growth years
    fade_period = fade_period  # The period after which the earnings growth starts to fade
    terminal_growth = terminal_growth / 100  # Terminal growth rate, assumed for the calculation

    tax_rate = 0.25  # Tax rate, derived from RoC post-tax formula
    roc_post_tax = roc_pre_tax * (1 - tax_rate)  # RoC post-tax
    reinvestment_rate_1 = initial_egv / roc_post_tax  # Reinvestment rate before fade period
    reinvestment_rate_2 = terminal_growth / roc_post_tax  # Reinvestment rate after fade period
    decline = (initial_egv - terminal_growth) / fade_period

    initial_nopat = 100 * roc_post_tax
    initial_investment = initial_nopat * reinvestment_rate_1
    initial_capital_ending = 100 + initial_investment

    years = list(range(0, growth_year + fade_period + 1))
    nopats = [initial_nopat]
    ebts = [initial_nopat / (1 - tax_rate)]
    investments = [initial_investment]
    fcfs = [initial_nopat - initial_investment]
    discount_factors = [1 / (1 + coc) ** n for n in years]
    discounted_fcfs = [fcfs[0] * discount_factors[0]]
    capital_endings = [initial_capital_ending]
    earning_growth_rates = [initial_egv]

    for n in range(1, len(years)):
        current_growth_rate = earning_growth_rates[n - 1] - decline if n > growth_year else initial_egv
        current_growth_rate = max(current_growth_rate, terminal_growth)
        earning_growth_rates.append(current_growth_rate)

        nopat = capital_endings[n - 1] * roc_post_tax
        nopats.append(nopat)

        ebt = nopat / (1 - tax_rate)
        ebts.append(ebt)

        investment_rate = reinvestment_rate_1 if n <= growth_year else earning_growth_rates[n] / roc_post_tax
        investment = nopat * investment_rate
        investments.append(investment)

        fcf = nopat - investment
        fcfs.append(fcf)

        discounted_fcf = fcf * discount_factors[n]
        discounted_fcfs.append(discounted_fcf)

        capital_ending = capital_endings[n - 1] + investment
        capital_endings.append(capital_ending)

    terminal_nopat = nopats[-1] * (1 + terminal_growth) / (coc - terminal_growth)
    terminal_investment = terminal_nopat * reinvestment_rate_2
    terminal_fcf = terminal_nopat - terminal_investment
    terminal_discounted_fcf = terminal_fcf * discount_factors[-1]

    intrinsic_value = sum(discounted_fcfs) + terminal_discounted_fcf
    intrinsic_pe = intrinsic_value / nopats[0]

    scrap = scrap
    current_pe = scrap['Stock P/E']
    fy23_pe = scrap['FY23 P/E']

    if current_pe < fy23_pe:
        overeval = (current_pe / round(intrinsic_pe, 2)) - 1
    else:
        overeval = (fy23_pe / round(intrinsic_pe, 2)) - 1

    return intrinsic_pe, overeval
