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
        self.flash_red = False

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
            
        frame = self.animations[self.state][int(self.frame_index)].copy()
        
        if self.flash_red:
            # Full Palette Surgical Flash: Target all green variants
            targets_light = [(157, 249, 228), (157, 248, 228)] # #9df9e4, #9df8e4
            targets_med   = [(123, 216, 196), (99, 185, 167)]  # #7bd8c4, #63b9a7
            targets_dark  = [(98, 184, 167), (103, 188, 170)]  # #62b8a7, #67bcaa
            
            flash_light = (255, 180, 180)
            flash_med   = (255, 50, 50)
            flash_dark  = (180, 0, 0)
            
            pixels = pygame.PixelArray(frame)
            for t in targets_light: pixels.replace(t, flash_light, distance=0.1)
            for t in targets_med: pixels.replace(t, flash_med, distance=0.1)
            for t in targets_dark: pixels.replace(t, flash_dark, distance=0.1)
            del pixels

        if self.flip:
            return pygame.transform.flip(frame, True, False)
        return frame
