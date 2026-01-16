class nation:
    def __init__(self, name, population, area, commercial, world_region=None):
        self.name = name
        self.population = population
        self.commercial = commercial
        self.area = area
        self.world_region = world_region
        
    
    
    def population_density(self):
        if self.area == 0:
            return 0
        return self.population / self.area
    
    def __str__(self):
        return f"Nation: {self.name}, Population: {self.population}, Area: {self.area}, Commercial: {self.commercial}, Region: {self.world_region}"