import taichi as ti
from types import SimpleNamespace
from Ecosystem import Ecosystem

def main() -> None:
    """ Initializes the taichi runtime and handles the main simulation loop """
    
    # Initializes taichi with GPU acceleration
    ti.init(arch=ti.gpu)
    
    # Simulation initial parameters
    simulation_values = SimpleNamespace(
        turn_factor = 0.5,
        perception_radius = 15.0,
        protected_range = 3.0,
        cohesion_weight = 0.03,
        alignment_weight = 0.08,
        separation_weight = 1.5,
        boids_max_speed = 1.5,
        predators_max_speed = 2.0,
        flee_weight = 0.01,
        chase_weight = 0.02,
        food_weight = 0.002,
        gravity_force = -0.02,
        dive_boost = 0.001
    )
    
    simulation_dimensions = SimpleNamespace(
        width=250.0, 
        height=250.0, 
        depth=250.0, 
        margin=5.0
    )
    
    # Initializing an Ecosystem
    ecosystem1 = Ecosystem(num_boids=5000, num_predators=10, num_food=20, dimensions=simulation_dimensions, simulation_values=simulation_values)
    
    ecosystem1.init()
    
    # Simulation objects
    window = ti.ui.Window("Boids 3D Simulation", (800, 800))
    canvas = window.get_canvas()
    scene = ti.ui.Scene()
    camera = ti.ui.Camera()
    
    gui = window.get_gui()
    
    camera.position(125, 125, 500)
    camera.lookat(125, 125, 125)
    
    while window.running:
        # Subwindow of the boids rules
        with gui.sub_window("Boids Rules", x=0.02, y=0.02, width=0.35, height=0.25):
            gui.text("Base Flocking Parameters")
            
            simulation_values.cohesion_weight = gui.slider_float("Cohesion", simulation_values.cohesion_weight, 0.0, 0.1)
            simulation_values.alignment_weight = gui.slider_float("Alignment", simulation_values.alignment_weight, 0.0, 0.2)
            simulation_values.separation_weight = gui.slider_float("Separation", simulation_values.separation_weight, 0.0, 4.0)
            
            gui.text("Vision & Speed")
            simulation_values.perception_radius = gui.slider_float("Sight Radius", simulation_values.perception_radius, 5.0, 30.0)
            simulation_values.protected_range = gui.slider_float("Personal Space", simulation_values.protected_range, 1.0, 10.0)
            simulation_values.boids_max_speed = gui.slider_float("Boid Max Speed", simulation_values.boids_max_speed, 0.5, 4.0)
        
        # Subwindow of the other ecosystem values
        with gui.sub_window("Ecosystem & Physics", x=0.02, y=0.40, width=0.25, height=0.40):
            gui.text("Survival Instincts")
            
            simulation_values.flee_weight = gui.slider_float("Fear", simulation_values.flee_weight, 0.0, 10.0)
            simulation_values.chase_weight = gui.slider_float("Predator Focus", simulation_values.chase_weight, 0.0, 0.2)
            simulation_values.food_weight = gui.slider_float("Hunger", simulation_values.food_weight, 0.0, 2.0)
            simulation_values.predators_max_speed = gui.slider_float("Predator Speed", simulation_values.predators_max_speed, 1.0, 5.0)
            
            gui.text("Environment")
            simulation_values.gravity_force = gui.slider_float("Gravity", simulation_values.gravity_force, -0.1, 0.0)
            simulation_values.dive_boost = gui.slider_float("Dive Speed Boost", simulation_values.dive_boost, 0.0, 3.0)
        
        # To update the simulation
        ecosystem1.setSimulationValues(simulation_values)
        ecosystem1.update()
        
        # Camera and simulation configurations
        camera.track_user_inputs(window, movement_speed=5.0, hold_key=ti.ui.RMB)
        scene.set_camera(camera)
        
        scene.ambient_light((0.5, 0.5, 0.5))
        scene.point_light(pos=(125, 300, 50), color=(1, 1, 1))
        
        # Update the screen particles according to the new values
        scene.particles(ecosystem1.boids_positions, radius=0.5, color=(0.0, 0.8, 1.0))
        if ecosystem1.num_predators > 0:
            scene.particles(ecosystem1.predators_positions, radius=1.2, color=(1.0, 0.0, 0.0))
        if ecosystem1.num_food > 0:
            scene.particles(ecosystem1.food_positions, radius=0.3, color=(0.0, 1.0, 0.0))
        
        canvas.scene(scene)
        window.show()
    
if __name__ == "__main__":
    main()