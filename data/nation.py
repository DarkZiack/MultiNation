class nation:
    def __init__(self, name, population, infrastructure, area, income, balance, commerce, commerce_buildings, 
                transport, transport_buildings, stability, stability_buildings, healthcare, healthcare_buildings
                , education, education_buildings, safety, safety_buildings , research_buildings, tourism_buildings, industrial,
                industrial_buildings, gdp, gdp_per_capita, tax, world_region=None):
        
        self.name = name
        self.population = population
        self.area = area
        self.infrastructure = infrastructure
        self.world_region = world_region
        self.population_density = self.calculate_density()
        self.income = income
        self.tax = tax
        self.balance = balance
        self.gdp = gdp
        self.gdp_per_capita = gdp_per_capita
        self.commerce = commerce
        self.commerce_buildings = commerce_buildings
        self.transport = transport
        self.transport_buildings = transport_buildings
        self.stability = stability
        self.stability_buildings = stability_buildings
        self.healthcare = healthcare
        self.healthcare_buildings = healthcare_buildings
        self.education = education
        self.education_buildings = education_buildings
        self.safety = safety
        self.safety_buildings = safety_buildings
        self.research_buildings = research_buildings
        self.tourism_buildings = tourism_buildings
        self.industrial = industrial
        self.industrial_buildings = industrial_buildings

    def calculate_density(self):
        if self.area > 0:
            return self.population / self.area
        return 0

    @property
    def building_slots(self):
        # Building slots based on infrastructure and area
        base_slots = 29
        infra_bonus = int(self.infrastructure / 100)  # 1 slot per 100 infrastructure
        area_bonus = int(self.area / 1000)  # 1 slot per 1000 sq km
        return base_slots + infra_bonus + area_bonus


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
