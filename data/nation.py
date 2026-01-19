class nation:
    def __init__(self, name, population, area, income, gdp, gdp_per_capita, world_region=None):
        self.name = name
        self.population = population
        self.area = area
        self.world_region = world_region
        self.population_density = self.calculate_density()
        self.income = income
        self.gdp = gdp
        self.gdp_per_capita = gdp_per_capita

    def calculate_density(self):
        if self.area > 0:
            return self.population / self.area
        return 0

    def update_economy(self, daily_income):
        self.income = daily_income
        self.gdp = daily_income * 365

        if self.population > 0:
            self.gdp_per_capita = self.gdp / self.population
        else:
            self.gdp_per_capita = 0

    def __str__(self):
        return (
            f"Nation: {self.name}"
            f"Population: {self.population} "
            f"Area: {self.area} sq km"
            f"Density: {self.population_density:.2f} people/sq km "
            f"Income: {self.income} ₽ "
            f"GDP: {self.gdp} ₽ "
            f"GDP per Capita: {self.gdp_per_capita} ₽ "
            f"Region: {self.world_region}"
        )
