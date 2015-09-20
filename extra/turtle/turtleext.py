"""This extension module port turtle to Scheme."""
# from berkeley's SICP course
import turtle
from tsi.expression import SNumber, SString, SPair, theNil
from tsi.procedure import SPrimitiveProc

tsi_ext_flag = None


def setup(env):
    procedures = (
        ('forward', forward), ('fd', forward),
        ('backward', backward), ('back', backward),
        ('left', left),
        ('right', right),
        ('circle', circle),
        ('setposition', setposition), ('setpos', setposition), ('set-pos', setposition),
        ('position', position), ('pos', position),
        ('heading', heading),
        ('setheading', setheading), ('set-heading', setheading),
        ('penup', penup), ('pu', penup), ('pen-up', penup),
        ('pendown', pendown), ('pd', pendown), ('pen-down', pendown),
        ('showturtle', showturtle), ('show-turtle', showturtle),
        ('hideturtle', hideturtle), ('hide-turtle', hideturtle),
        ('clear', clear),
        ('color', color),
        ('begin_fill', begin_fill), ('begin-fill', begin_fill),
        ('end_fill', end_fill), ('end-fill', end_fill),
        ('vec2d_abs', vec2d_abs), ('vec2d-abs', vec2d_abs),
        ('exitonclick', exitonclick), ('exit-on-click', exitonclick),
        ('speed', speed),
        ('tracer', tracer),
    )
    # add procedures to env
    env.extend((name, SPrimitiveProc(imp, name)) for (name, imp) in procedures)


def forward(n):
    """Move the turtle forward a distance N units on the current heading."""
    turtle.forward(n)
    return theNil


def backward(n):
    """Move the turtle backward a distance N units on the current heading,
    without changing direction."""
    turtle.backward(n)
    return theNil


def left(n):
    """Rotate the turtle's heading N degrees counterclockwise."""
    turtle.left(n)
    return theNil


def right(n):
    """Rotate the turtle's heading N degrees clockwise."""
    turtle.right(n)
    return theNil


def circle(r, extent=None):
    """Draw a circle with center R units to the left of the turtle (i.e.,
    right if N is negative. If EXTENT is not None, then draw EXTENT degrees
    of the circle only. Draws in the clockwise direction if R is negative,
    and otherwise counterclockwise, leaving the turtle facing along the
    arc at its end."""
    turtle.circle(r, extent)
    return theNil


def position():
    """Return current position as a pair."""
    return SPair(*turtle.position())


def heading():
    """Return current heading."""
    return SNumber(turtle.heading())


def vec2d_abs(v):
    abs_vec = abs(turtle.Vec2D(v.car, v.cdr))
    return SNumber(int(abs_vec))


def setposition(x_or_pos, y=None):
    """Set turtle's position to (X,Y), heading unchanged."""
    if y is None:
        if not isinstance(x_or_pos, SPair):
            raise Exception('pair expected')
        turtle.setposition(x_or_pos.car, x_or_pos.cdr)
    else:
        turtle.setposition(x_or_pos, y)
    return theNil


def setheading(h):
    """Set the turtle's heading H degrees clockwise from north (up)."""
    turtle.setheading(h)
    return theNil


def penup():
    """Raise the pen, so that the turtle does not draw."""
    turtle.penup()
    return theNil


def pendown():
    """Lower the pen, so that the turtle starts drawing."""
    turtle.pendown()
    return theNil


def showturtle():
    """Make turtle visible."""
    turtle.showturtle()
    return theNil


def hideturtle():
    """Make turtle invisible."""
    turtle.hideturtle()
    return theNil


def clear():
    """Clear the drawing, leaving the turtle unchanged."""
    turtle.clear()
    return theNil


def color(*args):
    """Set the color to C, a symbol such as red or '#ffc0c0' (representing
    hexadecimal red, green, and blue values."""
    if not args:
        return SPair(*map(SString, turtle.color()))
    for i in args:
        if not isinstance(i, SString):
            raise Exception('string expected')

    turtle.color(*map(str, args))
    return theNil


def begin_fill():
    """Start a sequence of moves that outline a shape to be filled."""
    turtle.begin_fill()
    return theNil


def end_fill():
    """Fill in shape drawn since last begin_fill."""
    turtle.end_fill()
    return theNil


def exitonclick():
    """Wait for a click on the turtle window, and then close it."""
    turtle.exitonclick()
    return theNil


def speed(s):
    """Set the turtle's animation speed as indicated by S (an integer in
    0-10, with 0 indicating no animation (lines draw instantly), and 1-10
    indicating faster and faster movement."""
    turtle.speed(s)
    return theNil


def tracer(n=None, delay=None):
    """If n is given, only each n-th regular screen update is really performed.
    Also set delay if given."""
    if n is None and delay is None:
        return SNumber(turtle.tracer())
    else:
        turtle.tracer(n, delay)
        return theNil
