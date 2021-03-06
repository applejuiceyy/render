from __future__ import annotations

import typing
from io import BytesIO
from typing import TYPE_CHECKING

import imageio
import numpy

if TYPE_CHECKING:
    from .scene import Scene


def run_scene(scene: Scene, io=None, *,
              format_if_animated="gif",
              format_if_static="png",
              callback: typing.Callable[[typing.IO, float], bool] = lambda *_: True,
              kwargs_if_animated: dict = None,
              kwargs_if_static: dict = None):
    first_frame = None
    first_duration = None

    if kwargs_if_static is None:
        kwargs_if_static = {}

    if kwargs_if_animated is None:
        kwargs_if_animated = {}

    if io is None:
        io = BytesIO()

    writer = None

    for image, duration in scene:
        if first_frame is None:
            first_frame = image.copy()
            first_duration = duration

        else:
            if writer is None:
                writer = imageio.get_writer(io, format_if_animated, **kwargs_if_animated)

                writer._duration = first_duration
                writer.append_data(numpy.array(first_frame))

                if not callback(io, scene.current_frame_second):
                    raise RuntimeError("Callback stopped execution")

            writer._duration = duration
            writer.append_data(numpy.array(image))

            if not callback(io, scene.current_frame_second):
                raise RuntimeError("Callback stopped execution")

    if writer is None:
        first_frame.save(io, format_if_static, **kwargs_if_static)

        if not callback(io, scene.current_frame_second):
            raise RuntimeError("Callback stopped execution")

    return io, writer is not None
