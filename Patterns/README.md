#  Software patterns

## Visitor

The assumption is that you have a class hierarchy that is fixed from another source and you cannot make changes to that code.

Visitor pattern defines the new behavior in a separate class called visitor, instead of trying to integrate it into existing classes.

Visitor pattern helps to add new behaviors or operations to a set of objects without modifying the original code of their classes.

Visitor involves defining a separate visitor class that implements the operations and accepting the visitor in the element classes.

The visitor interface should be declared with a set of visiting methods, one for each concrete element class in the program.

Declare the element interface with the acceptance method to accept the visitor object as an argument.

The acceptance method redirects the call to a visiting method on the incoming visitor object matching the class of the current element.

Visitors should only interact with the Element classes through the visitor interface.

Whenever a behavior cannot be implemented within an element hierarchy, create a new concrete visitor class and implement all of the visitor methods.
