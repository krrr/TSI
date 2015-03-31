"""This extension module port turtle to Scheme."""
# from berkeley's SICP course
import turtle
from tsi.expression import SNumber, SString, theNil
from tsi.procedure import SPrimitiveProc

tsi_ext_flag = None


def setup(env):
    pairs = [(name, SPrimitiveProc(imp, name)) for (name, imp) in _procedures]
    env.extend(pairs)


_turtle_screen_on = False


def _get_int(obj):
    if not isinstance(obj, SNumber):
        raise ValueError('number expected')
    return obj.num


def _check_screen():
    global _turtle_screen_on
    if not _turtle_screen_on:
        _turtle_screen_on = True
        turtle.title("Scheme Turtles")
        turtle.mode('logo')


def forward(n):
    """Move the turtle forward a distance N units on the current heading."""
    _check_screen()
    turtle.forward(_get_int(n))
    return theNil


def backward(n):
    """Move the turtle backward a distance N units on the current heading,
    without changing direction."""
    _check_screen()
    turtle.backward(_get_int(n))
    return theNil


def left(n):
    """Rotate the turtle's heading N degrees counterclockwise."""
    _check_screen()
    turtle.left(_get_int(n))
    return theNil


def right(n):
    """Rotate the turtle's heading N degrees clockwise."""
    _check_screen()
    turtle.right(_get_int(n))
    return theNil


def circle(r, extent=None):
    """Draw a circle with center R units to the left of the turtle (i.e.,
    right if N is negative. If EXTENT is not None, then draw EXTENT degrees
    of the circle only. Draws in the clockwise direction if R is negative,
    and otherwise counterclockwise, leaving the turtle facing along the
    arc at its end."""
    _check_screen()
    turtle.circle(_get_int(r), _get_int(extent) if extent else None)
    return theNil


def setposition(x, y):
    """Set turtle's position to (X,Y), heading unchanged."""
    _check_screen()
    turtle.setposition(_get_int(x), _get_int(y))
    return theNil


def setheading(h):
    """Set the turtle's heading H degrees clockwise from north (up)."""
    _check_screen()
    turtle.setheading(_get_int(h))
    return theNil


def penup():
    """Raise the pen, so that the turtle does not draw."""
    _check_screen()
    turtle.penup()
    return theNil


def pendown():
    """Lower the pen, so that the turtle starts drawing."""
    _check_screen()
    turtle.pendown()
    return theNil


def showturtle():
    """Make turtle visible."""
    _check_screen()
    turtle.showturtle()
    return theNil


def hideturtle():
    """Make turtle visible."""
    _check_screen()
    turtle.hideturtle()
    return theNil


def clear():
    """Clear the drawing, leaving the turtle unchanged."""
    _check_screen()
    turtle.clear()
    return theNil


def color(c):
    """Set the color to C, a symbol such as red or '#ffc0c0' (representing
    hexadecimal red, green, and blue values."""
    _check_screen()
    if not isinstance(c, SString):
        raise Exception('a string like "#FFFF00" expected')
    turtle.color(str(c))
    return theNil


def begin_fill():
    """Start a sequence of moves that outline a shape to be filled."""
    _check_screen()
    turtle.begin_fill()
    return theNil


def end_fill():
    """Fill in shape drawn since last begin_fill."""
    _check_screen()
    turtle.end_fill()
    return theNil


def exitonclick():
    """Wait for a click on the turtle window, and then close it."""
    global _turtle_screen_on
    if _turtle_screen_on:
        turtle.exitonclick()
        _turtle_screen_on = False
    return theNil


def speed(s):
    """Set the turtle's animation speed as indicated by S (an integer in
    0-10, with 0 indicating no animation (lines draw instantly), and 1-10
    indicating faster and faster movement."""
    _check_screen()
    turtle.speed(_get_int(s))
    return theNil


_procedures = (
    ('forward', forward),
    ('backward', backward), ('back', backward),
    ('left', left),
    ('right', right),
    ('circle', circle),
    ('setposition', setposition), ('setpos', setposition),
    ('setheading', setheading),
    ('penup', penup),
    ('pendown', pendown),
    ('showturtle', showturtle),
    ('hideturtle', hideturtle),
    ('clear', clear),
    ('color', color),
    ('begin_fill', begin_fill),
    ('end_fill', end_fill),
    ('exitonclick', exitonclick),
    ('speed', speed),
)
