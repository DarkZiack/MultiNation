class nation:
    def __init__(self, name, population, area, income, commerce, gdp, gdp_per_capita, tax, world_region=None):
        self.name = name
        self.population = population
        self.area = area
        self.world_region = world_region
        self.population_density = self.calculate_density()
        self.income = income
        self.gdp = gdp
        self.gdp_per_capita = gdp_per_capita
        self.commerce = commerce
        self.tax = tax

    def calculate_density(self):
        if self.area > 0:
            return self.population / self.area
        return 0


    def __str__(self):
        return (
            f"Nation: {self.name}"
            f"Population: {self.population} "
            f"Area: {self.area} sq km"
            f"Density: {self.population_density:.2f}"
            f"Income: {self.income}"
            f"GDP: {self.gdp}"
            f"GDP per Capita: {self.gdp_per_capita}"
            f"Region: {self.world_region}"
    
        )
