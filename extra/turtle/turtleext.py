"""This extension module port turtle to Scheme."""
# from berkeley's SICP course
import turtle
from tsi.expression import SNumber, SString, SPair, theNil
from tsi.primitives import SPrimitiveProc, extract_instance
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


def forward(operands, *__):
    """Move the turtle forward a distance N units on the current heading."""
    turtle.forward(*operands)
    return theNil


def backward(operands, *__):
    """Move the turtle backward a distance N units on the current heading,
    without changing direction."""
    turtle.backward(*operands)
    return theNil


def left(operands, *__):
    """Rotate the turtle's heading N degrees counterclockwise."""
    turtle.left(*operands)
    return theNil


def right(operands, *__):
    """Rotate the turtle's heading N degrees clockwise."""
    turtle.right(*operands)
    return theNil


def circle(operands, *__):
    """Draw a circle with center R units to the left of the turtle (i.e.,
    right if N is negative. If EXTENT is not None, then draw EXTENT degrees
    of the circle only. Draws in the clockwise direction if R is negative,
    and otherwise counterclockwise, leaving the turtle facing along the
    arc at its end."""
    turtle.circle(*operands)
    return theNil


def position(operands, *__):
    """Return current position as a pair."""
    return SPair(*turtle.position(*operands))


def heading(operands, *__):
    """Return current heading."""
    return SNumber(turtle.heading(*operands))


def vec2d_abs(operands, *__):
    v = extract_instance(operands, SPair)
    abs_vec = abs(turtle.Vec2D(v.car, v.cdr))
    return SNumber(abs_vec)


def setposition(operands, *__):
    """Set turtle's position to (X,Y), heading unchanged."""
    if len(operands) == 1:
        pos = extract_instance(operands, SPair)
        turtle.setposition(pos.car, pos.cdr)
    else:
        turtle.setposition(*operands)
    return theNil


def setheading(operands, *__):
    """Set the turtle's heading H degrees clockwise from north (up)."""
    turtle.setheading(*operands)
    return theNil


def penup(operands, *__):
    """Raise the pen, so that the turtle does not draw."""
    turtle.penup(*operands)
    return theNil


def pendown(operands, *__):
    """Lower the pen, so that the turtle starts drawing."""
    turtle.pendown(*operands)
    return theNil


def showturtle(operands, *__):
    """Make turtle visible."""
    turtle.showturtle(*operands)
    return theNil


def hideturtle(operands, *__):
    """Make turtle invisible."""
    turtle.hideturtle(*operands)
    return theNil


def clear(operands, *__):
    """Clear the drawing, leaving the turtle unchanged."""
    turtle.clear(*operands)
    return theNil


def color(operands, *__):
    """Set the color to C, a symbol such as red or '#ffc0c0' (representing
    hexadecimal red, green, and blue values."""
    if not operands:
        return SPair(*map(SString, turtle.color()))

    if not all(isinstance(i, SString) for i in operands):
        raise Exception('string expected')
    turtle.color(*map(str, operands))
    return theNil


def begin_fill(operands, *__):
    """Start a sequence of moves that outline a shape to be filled."""
    turtle.begin_fill(*operands)
    return theNil


def end_fill(operands, *__):
    """Fill in shape drawn since last begin_fill."""
    turtle.end_fill(*operands)
    return theNil


def exitonclick(operands, *__):
    """Wait for a click on the turtle window, and then close it."""
    turtle.exitonclick(*operands)
    return theNil


def speed(operands, *__):
    """Set the turtle's animation speed as indicated by S (an integer in
    0-10, with 0 indicating no animation (lines draw instantly), and 1-10
    indicating faster and faster movement."""
    turtle.speed(*operands)
    return theNil


def tracer(operands, *__):
    """If n is given, only each n-th regular screen update is really performed.
    Also set delay if given."""
    if not operands:
        return SNumber(turtle.tracer())
    else:
        turtle.tracer(*operands)
        return theNil
