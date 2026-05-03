from types import SimpleNamespace

import taichi as ti
import taichi.math as tm

@ti.data_oriented
class Ecosystem:
    
    def __init__(self, num_boids: int, num_predators: int, num_food: int, dimensions: SimpleNamespace, simulation_values: SimpleNamespace):
        """ Ecosystem class """
        
        # Grid variables 
        self.cell_size = 10.0
        self.max_boids_per_cell = 64
        
        # Defining the number of each object
        self.num_boids = num_boids
        self.num_predators = num_predators
        self.num_food = num_food
        
        # Variables that holds the positions of the elements in the simulation as Vectors
        # Boids
        self.boids_positions = ti.Vector.field(3, dtype=ti.float32, shape=num_boids)
        self.boids_velocity = ti.Vector.field(3, dtype=ti.float32, shape=num_boids)
        
        # Predators
        safe_num_predators = max(1, num_predators)
        self.predators_positions = ti.Vector.field(3, dtype=ti.float32, shape=safe_num_predators)
        self.predators_velocity = ti.Vector.field(3, dtype=ti.float32, shape=safe_num_predators)
        
        # Food
        safe_num_food = max(1, num_food)
        self.food_positions = ti.Vector.field(3, dtype=ti.float32, shape=safe_num_food)
        self.food_velocity = ti.Vector.field(3, dtype=ti.float32, shape=safe_num_food)
        
        # Initializing fields as 0D(Scalars) simulation values for the boids
        self.boids_max_speed = ti.field(dtype=ti.f32, shape=())
        self.turn_factor = ti.field(dtype=ti.f32, shape=())
        self.perception_radius = ti.field(dtype=ti.f32, shape=())
        self.protected_range = ti.field(dtype=ti.f32, shape=())
        
        self.cohesion_weight = ti.field(dtype=ti.f32, shape=())
        self.alignment_weight = ti.field(dtype=ti.f32, shape=())
        self.separation_weight = ti.field(dtype=ti.f32, shape=())
        
        # Scalar ecosystem values
        self.flee_weight = ti.field(dtype=ti.f32, shape=())
        self.chase_weight = ti.field(dtype=ti.f32, shape=())
        self.food_weight = ti.field(dtype=ti.f32, shape=())
        self.predators_max_speed = ti.field(dtype=ti.f32, shape=())
        
        self.gravity = ti.field(dtype=ti.f32, shape=())
        self.dive_boost = ti.field(dtype=ti.f32, shape=())
        
        # Defining the Uniform Spacial Grid
        self.grid_res = (int(dimensions.width / self.cell_size) + 1, int(dimensions.height / self.cell_size) + 1, int(dimensions.depth / self.cell_size) + 1, )
        
        self.grid_count = ti.field(dtype=ti.i32, shape=self.grid_res)
        self.grid_boids = ti.field(dtype=ti.i32, shape=(*self.grid_res, self.max_boids_per_cell))
        
        # Setting the values
        self.setDimensions(dimensions)
        self.setSimulationValues(simulation_values)
        
    def setDimensions(self, dims: SimpleNamespace) -> None:
        """ Dimensions setter """
        self.dim_width = dims.width
        self.dim_height = dims.height
        self.dim_depth = dims.depth
        self.dim_margin = dims.margin

    def setSimulationValues(self, sim_values: SimpleNamespace) -> None:
        """ Simulation values setter """
        self.boids_max_speed[None] = sim_values.boids_max_speed
        self.turn_factor[None] = sim_values.turn_factor
        self.perception_radius[None] = sim_values.perception_radius
        self.protected_range[None] = sim_values.protected_range
        
        self.cohesion_weight[None] = sim_values.cohesion_weight
        self.alignment_weight[None] = sim_values.alignment_weight
        self.separation_weight[None] = sim_values.separation_weight
        
        self.flee_weight[None] = sim_values.flee_weight
        self.chase_weight[None] = sim_values.chase_weight
        self.food_weight[None] = sim_values.food_weight
        self.predators_max_speed[None] = sim_values.predators_max_speed

        self.gravity[None] = sim_values.gravity_force
        self.dive_boost[None] = sim_values.dive_boost
    
    @ti.func
    def randomRange(self, low: int, top: int) -> None:
        """ Function that generates a random range for initialization of the particles """
        return ti.random() * (top - low) + low
    
    @ti.kernel
    def init(self):
        """ Function that initializes the simulation Vectors for each element """
        for i in range(self.num_boids):
            self.boids_positions[i] = tm.vec3(ti.random() * self.dim_width, ti.random() * self.dim_height, ti.random() * self.dim_depth)
            
            self.boids_velocity[i] = tm.vec3(self.randomRange(-1, 1), self.randomRange(-1, 1), self.randomRange(-1, 1)) * self.boids_max_speed[None]
        
        for i in range(self.num_predators):
            self.predators_positions[i] = tm.vec3(ti.random() * self.dim_width, ti.random() * self.dim_height, ti.random() * self.dim_depth)
            
            self.predators_velocity[i] = tm.vec3(self.randomRange(-1, 1), self.randomRange(-1, 1), self.randomRange(-1, 1)) * self.boids_max_speed[None]
        
        for i in range(self.num_food):
            self.food_positions[i] = tm.vec3(ti.random() * self.dim_width, ti.random() * self.dim_height, ti.random() * self.dim_depth)
            
            self.food_velocity[i] = tm.vec3(0.0, 0.0, 0.0)
    
    @ti.func
    def getGridIndex(self, pos):
        """ Returns the "box" index that an element is in the grid """
        x = ti.max(0, ti.min(int(pos[0] / self.cell_size), self.grid_res[0] - 1))
        y = ti.max(0, ti.min(int(pos[1] / self.cell_size), self.grid_res[1] - 1))
        z = ti.max(0, ti.min(int(pos[2] / self.cell_size), self.grid_res[2] - 1))
        
        return ti.Vector([x, y, z])
    
    @ti.func
    def updateGrid(self) -> None:
        """ Update the information on which cell each boid is """
        for i, j, k in self.grid_count:
            self.grid_count[i, j, k] = 0
        
        for i in range(self.num_boids):
            index = self.getGridIndex(self.boids_positions[i])
            
            count = ti.atomic_add(self.grid_count[index], 1)
            
            if count < self.max_boids_per_cell:
                self.grid_boids[index[0], index[1], index[2], count] = i
    
    @ti.func
    def computeEdgeSteering(self, pos):
        """ Calculate the steer force away from the border for each axis """
        edge_steer = ti.Vector([0.0, 0.0, 0.0])
        
        if pos[0] < self.dim_margin:
                edge_steer[0] += self.turn_factor[None]
        elif pos[0] > self.dim_width - self.dim_margin:
            edge_steer[0] -= self.turn_factor[None]
            
        if pos[1] < self.dim_margin:
            edge_steer[1] += self.turn_factor[None]
        elif pos[1] > self.dim_height - self.dim_margin:
            edge_steer[1] -= self.turn_factor[None]
                
        if pos[2] < self.dim_margin:
            edge_steer[2] += self.turn_factor[None]
        elif pos[2] > self.dim_depth - self.dim_margin:
            edge_steer[2] -= self.turn_factor[None]
        
        return edge_steer
   
    @ti.func
    def computeFlocking(self, i: int):
        """ To calculate Cohesion, alignment and separation behavior in flocks """
        neighbors = 0
        
        center_of_mass = ti.Vector([0.0, 0.0, 0.0])
        alignment = ti.Vector([0.0, 0.0, 0.0])
        
        separation_steer = ti.Vector([0.0, 0.0, 0.0])
        cohesion_steer = ti.Vector([0.0, 0.0, 0.0])
        alignment_steer = ti.Vector([0.0, 0.0, 0.0])
        
        boid_index = self.getGridIndex(self.boids_positions[i])
        
        # The 3x3 grid neighboring detection
        for dx in ti.static(range(-1, 2)):
            for dy in ti.static(range(-1, 2)):
                for dz in ti.static(range(-1, 2)):
                    neighbors_index = boid_index + ti.Vector([dx, dy, dz])
                    
                    if(0 <= neighbors_index[0] < self.grid_res[0] and 
                       0 <= neighbors_index[1] < self.grid_res[1] and
                       0 <= neighbors_index[2] < self.grid_res[2]
                       ):
                        cell_count = self.grid_count[neighbors_index]
                        
                        limit = ti.min(cell_count, self.max_boids_per_cell)
                        
                        for c in range(limit):
                            j = self.grid_boids[neighbors_index[0], neighbors_index[1], neighbors_index[2], c]
                            
                            if i != j:
                                difference = self.boids_positions[i] - self.boids_positions[j]
                                distance = difference.norm()
                                
                                if distance > 0.0001:
                                    if distance < self.perception_radius[None]:
                                        center_of_mass += self.boids_positions[j]
                                        alignment += self.boids_velocity[j]
                                        neighbors += 1
                                
                                    if distance < self.protected_range[None]:
                                        separation_steer += difference.normalized() / distance
        
        
        if neighbors > 0:
            center_of_mass = center_of_mass / neighbors
            desired_cohesion = (center_of_mass - self.boids_positions[i]).normalized()
            cohesion_steer = desired_cohesion - self.boids_velocity[i]
            
            average_velocity = (alignment / neighbors).normalized() * self.boids_max_speed[None]
            alignment_steer = average_velocity - self.boids_velocity[i]
        
        return cohesion_steer, alignment_steer, separation_steer               
    
    @ti.func
    def computeFleeing(self, i: int):
        """ Calculute the flee steering according to the distance of a boid from a predator """
        flee_steer = ti.Vector([0.0, 0.0, 0.0])
        
        for p in range(self.num_predators):
            difference = self.boids_positions[i] - self.predators_positions[p]
            distance = difference.norm()
            
            # The perception radius is multiplied by *2 as a "survival instinct"
            if distance > 0.0001 and distance < (self.perception_radius[None] * 2):
                flee_steer += difference.normalized() / distance
            
        return flee_steer
    
    @ti.func
    def computeHunting(self, p: int):
        """ Computing chase steer and single boid to persue based on distance """
        chase_steer = ti.Vector([0.0, 0.0, 0.0])
        closest_dist = self.perception_radius[None] * 3
        closest_prey = -1
        
        for j in range(self.num_boids):
            difference = self.predators_positions[p] - self.boids_positions[j]
            distance = difference.norm()
            
            if distance < closest_dist:
                closest_dist = distance
                closest_prey = j
        
        if closest_prey != -1:
            desired_velocity = (self.boids_positions[closest_prey] - self.predators_positions[p]).normalized() * self.predators_max_speed[None]
            chase_steer = desired_velocity - self.predators_velocity[p]
            
        return chase_steer
    
    @ti.func
    def computeForaging(self, i: int):
        """ Boids look for food """
        food_steer = ti.Vector([0.0, 0.0, 0.0])
        closest_dist = self.perception_radius[None] * 1.5
        closest_food = -1
        
        for f in range(self.num_food):
            difference = self.boids_positions[i] - self.food_positions[f]
            distance = difference.norm()
            
            if distance < closest_dist:
                closest_dist = distance
                closest_food = f
        
        if closest_food != -1:
            desired_velocity = (self.food_positions[closest_food] - self.boids_positions[i]).normalized() * self.boids_max_speed[None]
            food_steer = desired_velocity - self.boids_velocity[i]
        
        return food_steer
    
    @ti.kernel 
    def update(self):
        """ Main Kernel """
        
        # On each update call, updates the grid
        self.updateGrid()
        
        # Update the predators values
        for p in range(self.num_predators):
            chase = self.computeHunting(p)
            edges = self.computeEdgeSteering(self.predators_positions[p])
            
            self.predators_velocity[p] += (chase * self.chase_weight[None]) + edges
            
            current_max_speed = self.predators_max_speed[None]
            
            if self.predators_velocity[p][1] < 0:
                dive_intensity = -self.predators_velocity[p][1] / self.predators_velocity[p].norm()
                current_max_speed *= (1.0 + (dive_intensity * self.dive_boost[None]))
                self.predators_velocity[p][1] += self.gravity[None] * dive_intensity
            
            speed_norm = self.predators_velocity[p].norm()
            
            if speed_norm > self.predators_max_speed[None]:
                self.predators_velocity[p] = (self.predators_velocity[p] / speed_norm) * self.predators_max_speed[None]
            
            self.predators_positions[p] += self.predators_velocity[p]
        
        # Update the food values
        for f in range(self.num_food):
            self.food_velocity[f] += self.gravity[None] * 0.5
            self.food_velocity[f] += self.computeEdgeSteering(self.food_positions[f])
            self.food_positions[f] += self.food_velocity[f]
        
        # Update the boids values
        for i in range(self.num_boids):
            cohesion, alignment, separation = self.computeFlocking(i)
            flee = self.computeFleeing(i)
            food = self.computeForaging(i)
            edges = self.computeEdgeSteering(self.boids_positions[i])
            
            self.boids_velocity[i] += (cohesion * self.cohesion_weight[None]) + (alignment * self.alignment_weight[None]) + (separation * self.separation_weight[None]) + (flee * self.flee_weight[None]) + (food * self.food_weight[None]) + edges

            current_max_speed = self.boids_max_speed[None]
            
            if self.boids_velocity[i][1] < 0:
                dive_intensity = -self.boids_velocity[i][1] / self.boids_velocity[i].norm()
                current_max_speed *= (1.0 + (dive_intensity * self.dive_boost[None]))
                self.boids_velocity[i][1] += self.gravity[None] * dive_intensity
            
            speed_norm = self.boids_velocity[i].norm()
            
            if speed_norm > self.boids_max_speed[None]:
                self.boids_velocity[i] = (self.boids_velocity[i] / speed_norm) * self.boids_max_speed[None]
            
            self.boids_positions[i] += self.boids_velocity[i]