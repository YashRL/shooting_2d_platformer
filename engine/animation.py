import pygame

class AnimationManager:
    def __init__(self, frames_dict, animation_speed=0.15):
        """
        frames_dict: { 'state_name': [Surface1, Surface2, ...] }
        """
        self.animations = frames_dict
        self.state = list(frames_dict.keys())[0] if frames_dict else None
        self.frame_index = 0
        self.animation_speed = animation_speed
        self.flip = False

    def change_state(self, new_state):
        if self.state != new_state:
            self.state = new_state
            self.frame_index = 0

    def update(self):
        if not self.state or self.state not in self.animations:
            return
            
        self.frame_index += self.animation_speed
        if self.frame_index >= len(self.animations[self.state]):
            self.frame_index = 0

    def get_current_frame(self):
        if not self.state or self.state not in self.animations:
            return None
            
        frame = self.animations[self.state][int(self.frame_index)]
        if self.flip:
            return pygame.transform.flip(frame, True, False)
        return frame
