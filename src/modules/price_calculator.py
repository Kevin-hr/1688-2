"""
价格计算模块 - Ozon卢布定价计算
"""


class PriceCalculator:
    """
    Ozon 价格计算器

    基于成本预估模型的卢布定价机制
    包含：采购价、国内物流、国际物流、汇率与毛利率
    """

    # 默认参数
    DEFAULT_EXCHANGE_RATE = 13.0  # 1 CNY ≈ 13 RUB
    DEFAULT_PROFIT_MARGIN = 0.40  # 40% 毛利率
    DEFAULT_DOMESTIC_SHIPPING = 3.0  # 国内快递 3 CNY
    DEFAULT_INTL_SHIPPING_PER_KG = 45.0  # 国际物流 45 CNY/kg

    def __init__(
        self,
        exchange_rate: float = None,
        profit_margin: float = None,
        domestic_shipping: float = None,
        intl_shipping_per_kg: float = None
    ):
        """
        初始化计算器

        Args:
            exchange_rate: CNY→RUB 汇率
            profit_margin: 毛利率 (0.4 = 40%)
            domestic_shipping: 国内快递成本 (CNY)
            intl_shipping_per_kg: 国际物流每公斤成本 (CNY)
        """
        self.exchange_rate = exchange_rate or self.DEFAULT_EXCHANGE_RATE
        self.profit_margin = profit_margin or self.DEFAULT_PROFIT_MARGIN
        self.domestic_shipping = domestic_shipping or self.DEFAULT_DOMESTIC_SHIPPING
        self.intl_shipping_per_kg = intl_shipping_per_kg or self.DEFAULT_INTL_SHIPPING_PER_KG

    def calculate(
        self,
        cny_price: float,
        weight_g: float = None,
        weight_kg: float = None
    ) -> int:
        """
        计算最终售价（卢布）

        公式:
        total_cost = cny_price + domestic_shipping + intl_shipping
        final_price = total_cost * exchange_rate * (1 + profit_margin)

        Args:
            cny_price: 商品采购价 (CNY)
            weight_g: 商品重量 (克)
            weight_kg: 商品重量 (千克)，优先于 weight_g

        Returns:
            最终售价（卢布，整数）
        """
        # 处理价格
        if not cny_price or cny_price <= 0:
            cny_price = 10.0  # 兜底

        # 处理重量
        if weight_kg is None:
            weight_kg = (weight_g or 500) / 1000.0

        # 计算国际物流成本
        intl_shipping = weight_kg * self.intl_shipping_per_kg

        # 总成本
        total_cost = cny_price + self.domestic_shipping + intl_shipping

        # 最终售价
        final_price = total_cost * self.exchange_rate * (1 + self.profit_margin)

        return int(final_price)

    def calculate_with_details(
        self,
        cny_price: float,
        weight_g: float = None
    ) -> dict:
        """
        计算并返回详细明细

        Args:
            cny_price: 商品采购价 (CNY)
            weight_g: 商品重量 (克)

        Returns:
            包含所有计算明细的字典
        """
        weight_kg = (weight_g or 500) / 1000.0

        # 各项成本
        domestic = self.domestic_shipping
        intl = weight_kg * self.intl_shipping_per_kg

        # 总成本
        total_cny = cny_price + domestic + intl

        # 售价
        total_rub = total_cny * self.exchange_rate
        final_rub = int(total_rub * (1 + self.profit_margin))

        # 利润
        profit = final_rub - (total_cny * self.exchange_rate)

        return {
            "cny_price": cny_price,
            "domestic_shipping": domestic,
            "intl_shipping": intl,
            "total_cost_cny": total_cny,
            "exchange_rate": self.exchange_rate,
            "profit_margin": self.profit_margin,
            "price_rub": final_rub,
            "profit_rub": profit,
        }

    def estimate_profit_margin(
        self,
        cny_price: float,
        weight_g: float,
        sell_price_rub: float
    ) -> float:
        """
        估算实际毛利率

        Args:
            cny_price: 采购价 (CNY)
            weight_g: 重量 (克)
            sell_price_rub: 销售价 (RUB)

        Returns:
            毛利率 (0.4 = 40%)
        """
        weight_kg = weight_g / 1000.0
        cost = cny_price + self.domestic_shipping + (weight_kg * self.intl_shipping_per_kg)
        cost_rub = cost * self.exchange_rate

        if cost_rub <= 0:
            return 0.0

        return (sell_price_rub - cost_rub) / sell_price_rub


# 便捷函数
def calculate_price(cny_price: float, weight_g: float = None) -> int:
    """快速价格计算"""
    calculator = PriceCalculator()
    return calculator.calculate(cny_price, weight_g)


if __name__ == "__main__":
    # 测试
    calc = PriceCalculator()

    # 测试用例
    test_cases = [
        {"price": 3.7, "weight": 50},    # 低价轻量
        {"price": 50, "weight": 500},    # 中价中量
        {"price": 100, "weight": 2000},   # 高价重量
    ]

    print("价格计算测试:")
    for case in test_cases:
        details = calc.calculate_with_details(case["price"], case["weight"])
        print(f"\n采购价: {details['cny_price']} CNY, 重量: {case['weight']}g")
        print(f"  国内物流: {details['domestic_shipping']} CNY")
        print(f"  国际物流: {details['intl_shipping']:.2f} CNY")
        print(f"  总成本: {details['total_cost_cny']:.2f} CNY")
        print(f"  售价: {details['price_rub']} RUB")
        print(f"  预计利润: {details['profit_rub']:.0f} RUB")
