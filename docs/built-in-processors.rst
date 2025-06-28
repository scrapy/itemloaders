.. _built-in-processors:

Available built-in processors
=============================

Even though you can use any callable function as input and output processors,
``itemloaders`` provides some commonly used processors, which are described
below.

Some of them, like the :class:`~itemloaders.processors.MapCompose` (which is
typically used as input processor) compose the output of several functions
executed in order, to produce the final parsed value.

Here is a list of all built-in processors:

.. automodule:: itemloaders.processors
    :members:
