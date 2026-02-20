import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class nation:
    name: str
    population: float = 0.0
    infrastructure: float = 0.0
    area: float = 0.0
    income: float = 0.0
    balance: float = 0.0
    tech_income: float = 0.0
    tech_balance: float = 0.0
    commerce: float = 0.0
    commerce_buildings: int = 0
    transport: float = 0.0
    transport_buildings: int = 0
    stability: float = 0.0
    stability_buildings: int = 0
    healthcare: float = 0.0
    healthcare_buildings: int = 0
    education: float = 0.0
    education_buildings: int = 0
    safety: float = 0.0
    safety_buildings: int = 0
    research_buildings: int = 0
    historic_buildings: int = 0
    industrial: float = 0.0
    industrial_buildings: int = 0
    gdp: float = 0.0
    gdp_per_capita: float = 0.0
    tax: float = 0.0
    military_base: int = 0
    air_base: int = 0
    naval_base: int = 0
    world_region: Optional[str] = None
    last_save_time: float = field(default_factory=time.time)

    # Military counts (initialized to zero to avoid unbound attribute bugs)
    soldiers: int = 0
    tanks: int = 0
    artillery: int = 0
    motorized: int = 0
    bomber: int = 0
    fighter: int = 0
    helicopter: int = 0
    submarine: int = 0
    destroyer: int = 0
    battleship: int = 0
    carrier: int = 0
    # Tech upgrade levels for each building/unit type
    tech_upgrades: dict = field(default_factory=lambda: {
        "commerce": 0,
        "transport": 0,
        "stability": 0,
        "healthcare": 0,
        "education": 0,
        "safety": 0,
        "research": 0,
        "historic": 0,
        "industrial": 0,
        "infrastructure_cost": 0,
        "land_cost": 0,
        "tech_gain": 0,
        "tech_cost": 0,
        "building_slots": 0,
        "military_base": 0,
        "air_base": 0,
        "naval_base": 0,
        "soldiers": 0,
        "tanks": 0,
        "artillery": 0,
        "motorized": 0,
        "bomber": 0,
        "fighter": 0,
        "helicopter": 0,
        "submarine": 0,
        "destroyer": 0,
        "battleship": 0,
        "carrier": 0,
    })

    def __post_init__(self):
        self.population_density = self.calculate_density()

    def calculate_density(self) -> float:
        return (self.population / self.area) if self.area > 0 else 0.0

    @property
    def building_slots(self) -> int:
        base_slots = 29
        infra_bonus = int(self.infrastructure / 100)
        area_bonus = int(self.area / 1000)
        tech_bonus = int(self.get_tech_level("building_slots") * 2)
        return base_slots + infra_bonus + area_bonus + tech_bonus

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "population": self.population,
            "population_density": self.population_density,
            "income": self.income,
            "balance": self.balance,
            "tech_income": self.tech_income,
            "tech": self.tech_balance,
            "gdp": self.gdp,
            "gdp_per_capita": self.gdp_per_capita,
            "area": self.area,
            "infrastructure": self.infrastructure,
            "world_region": self.world_region,
            "tax": self.tax,
            "commerce": self.commerce,
            "commerce_buildings": self.commerce_buildings,
            "transport": self.transport,
            "transport_buildings": self.transport_buildings,
            "stability": self.stability,
            "stability_buildings": self.stability_buildings,
            "healthcare": self.healthcare,
            "healthcare_buildings": self.healthcare_buildings,
            "education": self.education,
            "education_buildings": self.education_buildings,
            "safety": self.safety,
            "safety_buildings": self.safety_buildings,
            "research_buildings": self.research_buildings,
            "historic_buildings": self.historic_buildings,
            "industrial": self.industrial,
            "industrial_buildings": self.industrial_buildings,
            "military_base": self.military_base,
            "air_base": self.air_base,
            "naval_base": self.naval_base,
            "last_save_time": self.last_save_time,
            "soldiers": self.soldiers,
            "tanks": self.tanks,
            "artillery": self.artillery,
            "motorized": self.motorized,
            "bomber": self.bomber,
            "fighter": self.fighter,
            "helicopter": self.helicopter,
            "submarine": self.submarine,
            "destroyer": self.destroyer,
            "battleship": self.battleship,
            "carrier": self.carrier,
            "tech_upgrades": self.tech_upgrades,
        }

    @classmethod
    def from_dict(cls, d: dict):
        return cls(
            name=d.get("name"),
            population=d.get("population", 0.0),
            infrastructure=d.get("infrastructure", 0.0),
            area=d.get("area", 0.0),
            income=d.get("income", 0.0),
            balance=d.get("balance", 0.0),
            tech_income=d.get("tech_income", 0.0),
            tech_balance=d.get("tech", d.get("tech_balance", 0.0)),
            commerce=d.get("commerce", 0.0),
            commerce_buildings=d.get("commerce_buildings", 0),
            transport=d.get("transport", 0.0),
            transport_buildings=d.get("transport_buildings", 0),
            stability=d.get("stability", 0.0),
            stability_buildings=d.get("stability_buildings", 0),
            healthcare=d.get("healthcare", 0.0),
            healthcare_buildings=d.get("healthcare_buildings", 0),
            education=d.get("education", 0.0),
            education_buildings=d.get("education_buildings", 0),
            safety=d.get("safety", 0.0),
            safety_buildings=d.get("safety_buildings", 0),
            research_buildings=d.get("research_buildings", 0),
            historic_buildings=d.get("historic_buildings", 0),
            industrial=d.get("industrial", 0.0),
            industrial_buildings=d.get("industrial_buildings", 0),
            gdp=d.get("gdp", 0.0),
            gdp_per_capita=d.get("gdp_per_capita", 0.0),
            tax=d.get("tax", 0.0),
            military_base=d.get("military_base", 0),
            air_base=d.get("air_base", 0),
            naval_base=d.get("naval_base", 0),
            world_region=d.get("world_region"),
            last_save_time=d.get("last_save_time", None),
            soldiers=d.get("soldiers", 0),
            tanks=d.get("tanks", 0),
            artillery=d.get("artillery", 0),
            motorized=d.get("motorized", 0),
            bomber=d.get("bomber", 0),
            fighter=d.get("fighter", 0),
            helicopter=d.get("helicopter", 0),
            submarine=d.get("submarine", 0),
            destroyer=d.get("destroyer", 0),
            battleship=d.get("battleship", 0),
            carrier=d.get("carrier", 0),
            tech_upgrades=d.get("tech_upgrades", {}),
        )

    # Tech helpers
    def get_tech_level(self, key: str) -> int:
        return int(self.tech_upgrades.get(key, 0))

    def get_tech_multiplier(self, key: str, per_level: float = 0.05) -> float:
        # Default: each tech level gives +5% effectiveness
        return 1.0 + (self.get_tech_level(key) * per_level)

    def get_cost_multiplier(self, key: str, per_level: float = None, min_mult: float = 0.2) -> float:
        """Return a multiplier applied to costs for `key` where higher tech levels reduce cost.
        By default land and infrastructure tech give 0.5% discount per level; other techs give 5%.
        Example: level 1 with per_level=0.05 -> multiplier 0.95 (5% discount). Capped by `min_mult`.
        """
        # Default per-level discounts: 0.5% for land/infra, 5% for others
        if per_level is None:
            per_level = 0.005 if key in ("land_cost", "infrastructure_cost") else 0.05
        level = self.get_tech_level(key)
        mult = 1.0 - (level * per_level)
        return max(mult, float(min_mult))

    def upgrade_tech(self, key: str, levels: int = 1) -> int:
        self.tech_upgrades[key] = self.get_tech_level(key) + int(levels)
        return self.tech_upgrades[key]

    # Scalable upgrade costs and purchase helpers
    def tech_cost_for_level(self, base_cost: float = 1000.0, growth: float = 2.25, level: int = 1) -> float:
        """Cost for a specific absolute level (1-based)."""
        if level < 1:
            return 0.0
        return base_cost * (growth ** (level - 1))

    def next_level_cost(self, key: str, base_cost: float = 1000.0, growth: float = 2.25, max_level: int = None) -> float:
        """Cost to purchase the next single tech level for `key`.
        If `max_level` is provided and reached, returns 0.0. If `max_level` is None, tech is uncapped.
        """
        current = self.get_tech_level(key)
        if max_level is not None and current >= max_level:
            return 0.0
        return self.tech_cost_for_level(base_cost=base_cost, growth=growth, level=current + 1)

    def total_cost_for_levels(self, key: str, additional_levels: int = 1, base_cost: float = 1000.0, growth: float = 2.25, max_level: int = None) -> float:
        """Total cost to buy `additional_levels` starting from current level.
        If `max_level` provided, caps at that level; otherwise uncapped.
        """
        current = self.get_tech_level(key)
        if additional_levels <= 0:
            return 0.0
        if max_level is not None and current >= max_level:
            return 0.0
        if max_level is None:
            target = current + additional_levels
        else:
            target = min(max_level, current + additional_levels)
        total = 0.0
        for lvl in range(current + 1, target + 1):
            total += self.tech_cost_for_level(base_cost=base_cost, growth=growth, level=lvl)
        return total

    def purchase_tech(self, key: str, levels: int = 1, base_cost: float = 1000.0, growth: float = 2.25, max_level: int = None) -> bool:
        """Attempt to purchase `levels` of tech for `key` using tech currency (`tech_balance`).
        Deducts `tech_balance` if affordable and returns True. Returns False if not enough tech
        or already at max level.
        """
        if levels <= 0:
            return False
        current = self.get_tech_level(key)
        if max_level is not None and current >= max_level:
            return False
        total = self.total_cost_for_levels(key, additional_levels=levels, base_cost=base_cost, growth=growth, max_level=max_level)
        if total <= 0:
            return False
        # Apply global tech-purchase discount if present (tech key: 'tech_cost')
        discount = self.get_cost_multiplier('tech_cost', per_level=0.05, min_mult=0.2)
        total *= discount
        # Use tech_balance (not money balance) for tech purchases
        if self.tech_balance >= total:
            self.tech_balance -= total
            # Determine how many levels were actually purchased (handle uncapped tech)
            if max_level is None:
                purchased = levels
            else:
                purchased = min(levels, max_level - current)
            if purchased <= 0:
                return False
            self.upgrade_tech(key, purchased)
            return True
        return False