import time
from gurobipy import GRB, Model

# Example data

capacity_in_supplier = {'supplier1': 150, 'supplier2': 50, 'supplier3': 100}

shipping_cost_from_supplier_to_DC = {
    ('supplier1', 'CDC'): 5,
    ('supplier1', 'LDC'): 4,
    ('supplier2', 'CDC'): 6,
    ('supplier2', 'LDC'): 3,
    ('supplier3', 'CDC'): 2,
    ('supplier3', 'LDC'): 7
}

roasting_cost_light = {'CDC': 3, 'LDC': 5}

roasting_cost_dark = {'CDC': 5, 'LDC': 6}

shipping_cost_from_DC_to_cafe = {
    ('CDC', 'Berlin-CS'): 5,
    ('CDC', 'Paris-CS'): 3,
    ('CDC', 'LDN-CS'): 6,
    ('LDC', 'Berlin-CS'): 4,
    ('LDC', 'Paris-CS'): 5,
    ('LDC', 'LDN-CS'): 2
}

light_coffee_needed_for_cafe = {'Berlin-CS': 20, 'Paris-CS': 30, 'LDN-CS': 40}

dark_coffee_needed_for_cafe = {'Berlin-CS': 20, 'Paris-CS': 20, 'LDN-CS': 100}

cafes = list(set(i[1] for i in shipping_cost_from_DC_to_cafe.keys()))
roasteries = list(
    set(i[1] for i in shipping_cost_from_supplier_to_DC.keys()))
suppliers = list(
    set(i[0] for i in shipping_cost_from_supplier_to_DC.keys()))

# Create a new model
model = Model("coffee_distribution")

# OPTIGUIDE DATA CODE GOES HERE

# Create variables
x = model.addVars(shipping_cost_from_supplier_to_DC.keys(),
                  vtype=GRB.INTEGER,
                  name="x")
y_light = model.addVars(shipping_cost_from_DC_to_cafe.keys(),
                        vtype=GRB.INTEGER,
                        name="y_light")
y_dark = model.addVars(shipping_cost_from_DC_to_cafe.keys(),
                       vtype=GRB.INTEGER,
                       name="y_dark")

# Set objective
model.setObjective(
    sum(x[i] * shipping_cost_from_supplier_to_DC[i]
        for i in shipping_cost_from_supplier_to_DC.keys()) +
    sum(roasting_cost_light[r] * y_light[r, c] +
        roasting_cost_dark[r] * y_dark[r, c]
        for r, c in shipping_cost_from_DC_to_cafe.keys()) + sum(
            (y_light[j] + y_dark[j]) * shipping_cost_from_DC_to_cafe[j]
            for j in shipping_cost_from_DC_to_cafe.keys()), GRB.MINIMIZE)

# Conservation of flow constraint
for r in set(i[1] for i in shipping_cost_from_supplier_to_DC.keys()):
    model.addConstr(
        sum(x[i] for i in shipping_cost_from_supplier_to_DC.keys()
            if i[1] == r) == sum(
                y_light[j] + y_dark[j]
                for j in shipping_cost_from_DC_to_cafe.keys()
                if j[0] == r), f"flow_{r}")

# Add supply constraints
for s in set(i[0] for i in shipping_cost_from_supplier_to_DC.keys()):
    model.addConstr(
        sum(x[i] for i in shipping_cost_from_supplier_to_DC.keys()
            if i[0] == s) <= capacity_in_supplier[s], f"supply_{s}")

# Add demand constraints
for c in set(i[1] for i in shipping_cost_from_DC_to_cafe.keys()):
    model.addConstr(
        sum(y_light[j] for j in shipping_cost_from_DC_to_cafe.keys()
            if j[1] == c) >= light_coffee_needed_for_cafe[c],
        f"light_demand_{c}")
    model.addConstr(
        sum(y_dark[j] for j in shipping_cost_from_DC_to_cafe.keys()
            if j[1] == c) >= dark_coffee_needed_for_cafe[c],
        f"dark_demand_{c}")

# Optimize model
model.optimize()
m = model

# OPTIGUIDE CONSTRAINT CODE GOES HERE

# Solve
m.update()
model.optimize()

print(time.ctime())
if m.status == GRB.OPTIMAL:
    print(f'Optimal cost: {m.objVal}')
else:
    print("Not solved to optimality. Optimization status:", m.status)
