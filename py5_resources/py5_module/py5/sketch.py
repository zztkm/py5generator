# -*- coding: utf-8 -*-
# *** FORMAT PARAMS ***
import time
import io
import json
from pathlib import Path
from typing import overload, NewType, Any, Callable, Union, Dict, List  # noqa

import numpy as np

from PIL import Image
import cairosvg

from jnius import autoclass  # noqa

from .methods import Py5Methods, Py5Exception  # noqa
from .java_types import _Py5Applet, Py5Applet  # noqa
from .java_types import *  # noqa
from .converter import Converter  # noqa

class_members_code = None  # DELETE

_METHODS = ['settings', 'setup', 'draw', 'key_pressed', 'key_typed',
            'key_released', 'mouse_clicked', 'mouse_dragged', 'mouse_moved',
            'mouse_entered', 'mouse_exited', 'mouse_pressed', 'mouse_released',
            'mouse_wheel', 'exit_actual']


class Sketch:

    def __init__(self):
        self._py5applet = _Py5Applet()
        self._converter = Converter(self._py5applet)
        self._pimage_cache = dict()
        self._pshape_cache = dict()
        self._methods_to_profile = []
        # must always keep the py5_methods reference count from hitting zero.
        # otherwise, it will be garbage collected and lead to segmentation faults!
        self._py5_methods = None

    def run_sketch(self, block: bool = True) -> None:
        methods = dict([(e, getattr(self, e)) for e in _METHODS if hasattr(self, e)])
        self._run_sketch(methods, block)

    def _run_sketch(self, methods: Dict[str, Callable], block: bool) -> None:
        self._py5_methods = Py5Methods(self)
        self._py5_methods.set_functions(**methods)
        self._py5_methods.profile_functions(self._methods_to_profile)
        self._py5applet.usePy5Methods(self._py5_methods)

        _Py5Applet.runSketch([''], self._py5applet)

        if block:
            # wait for the sketch to finish
            surface = self.get_surface()
            while not surface.isStopped():
                time.sleep(0.25)

    def exit_sketch(self) -> None:
        """Exit the sketch
        """
        if not self.get_surface().isStopped():
            self._py5applet.exit()

    def get_py5applet(self) -> Py5Applet:
        return self._py5applet

    def hot_reload_draw(self, draw):
        self._py5_methods.set_functions(**dict(draw=draw))

    def profile_functions(self, function_names):
        if self._py5_methods is None:
            self._methods_to_profile.extend(function_names)
        else:
            self._py5_methods.profile_functions(function_names)

    def profile_draw(self):
        self.profile_functions(['draw'])

    def print_line_profiler_stats(self):
        self._py5_methods.dump_stats()

    # *** Pixel methods ***

    def get_pixels(self) -> np.ndarray:
        pixels = np.frombuffer(self._py5applet.loadAndGetPixels().tostring(), dtype=np.uint8)
        return pixels.reshape(self.height, self.width, 4).copy()

    def set_pixels(self, new_pixels: np.ndarray):
        self._py5applet.setAndUpdatePixels(new_pixels.flatten().tobytes(), pass_by_reference=False)

    # *** PImage replacement methods ***

    @overload
    def image(self, img: Any, a: float, b: float, cache: bool) -> None:
        """$class_image"""
        pass

    @overload
    def image(self, img: Any, a: float, b: float, c: float, d: float, cache: bool) -> None:
        """$class_image"""
        pass

    def image(self, *args, cache: bool = False) -> None:
        """$class_image"""
        arg0_id = id(args[0])
        if cache and arg0_id in self._pimage_cache:
            pimage = self._pimage_cache[arg0_id]
        else:
            pimage = self._converter.to_pimage(args[0])

        if cache:
            self._pimage_cache[arg0_id] = pimage

        self._py5applet.image(pimage, *args[1:])

    # TODO: what about alpha mask images?
    # TODO: are there other PImage functions I should be paying attention to?
    # TODO: does caching actually work?

    def create_image(self, mode: str, width: int, height: int, color: Any) -> Image.Image:
        """$class_create_image"""
        return Image.new(mode, (width, height), color)

    def load_image(self, filename: Union[str, Path]) -> Image.Image:
        """$class_load_image"""
        filename = Path(filename)
        if filename.suffix.lower() == '.svg':
            with open(filename, 'r') as f:
                return Image.open(io.BytesIO(cairosvg.svg2png(file_obj=f)))
        else:
            return Image.open(filename)

    def texture(self, image: Any, cache: bool = False) -> None:
        """$class_texture"""
        image_id = id(image)
        if cache and image_id in self._pimage_cache:
            pimage = self._pimage_cache[image_id]
        else:
            pimage = self._converter.to_pimage(image)
        if cache:
            self._pimage_cache[image_id] = pimage

        self._py5applet.texture(pimage)

    # *** Math (numpy) methods ***

    @classmethod
    def sin(cls, angle: float) -> float:
        return np.sin(angle)

    @classmethod
    def cos(cls, angle: float) -> float:
        return np.cos(angle)

    @classmethod
    def tan(cls, angle: float) -> float:
        return np.tan(angle)

    @classmethod
    def asin(cls, value: float) -> float:
        return np.arcsin(value)

    @classmethod
    def acos(cls, value: float) -> float:
        return np.arccos(value)

    @classmethod
    def atan(cls, value: float) -> float:
        return np.arctan(value)

    @classmethod
    def atan2(cls, y: float, x: float) -> float:
        return np.arctan2(y, x)

    @classmethod
    def degrees(cls, radians: float) -> float:
        return np.degrees(radians)

    @classmethod
    def radians(cls, degrees: float) -> float:
        return np.radians(degrees)

    @classmethod
    def constrain(cls, amt: float, low: float, high: float) -> float:
        return np.where(amt < low, low, np.where(amt > high, high, amt))

    @classmethod
    def dist(cls, *args) -> float:
        p1 = args[:(len(args) // 2)]
        p2 = args[(len(args) // 2):]
        assert len(p1) == len(p2)
        return sum([(a - b)**2 for a, b in zip(p1, p2)])**0.5

    @classmethod
    def lerp(cls, start: float, stop: float, amt: float):
        return amt * (stop - start) + start

    @classmethod
    def mag(cls, *args) -> float:
        return sum([x * x for x in args])**0.5

    @classmethod
    def norm(cls, value: float, start: float, stop: float) -> float:
        return (value - start) / (stop - start)

    @classmethod
    def sq(cls, n: float) -> float:
        return n * n

    # *** JSON methods ***

    @classmethod
    def load_json(cls, filename: Union[str, Path], **kwargs: Dict[str, Any]) -> Any:
        with open(filename, 'r') as f:
            return json.load(f, **kwargs)

    @classmethod
    def save_json(cls, json_data: Any, filename: Union[str, Path], **kwargs: Dict[str, Any]):
        with open(filename, 'w') as f:
            json.dump(json_data, f, **kwargs)

    @classmethod
    def parse_json(cls, serialized_json: Any, **kwargs: Dict[str, Any]) -> Any:
        return json.loads(serialized_json, **kwargs)


{class_members_code}