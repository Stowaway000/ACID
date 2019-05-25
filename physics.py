import cocos.euclid as eu
import cocos.collision_model as cm
import cocos

class collision_unit():
    def __init__(self, obj, type):
        if type == "rect":
            center = (obj.position[0]+obj.size[0]/2, obj.position[1]+obj.size[1]/2)
            self.cshape = cm.AARectShape(center, obj.size[0]/2, obj.size[1]/2)
        elif type == "circle":
            self.cshape = cm.CircleShape(obj[0], obj[1])

        elif type == "bullet":
            self.cshape = cm.CircleShape()

class circle_map_collider():
    def __init__(self, maplayer):
        self.collision_manager = cm.CollisionManagerBruteForce()
        for obj in maplayer.layer_collision.objects:
            block = collision_unit(obj, "rect")
            self.collision_manager.add(block)
