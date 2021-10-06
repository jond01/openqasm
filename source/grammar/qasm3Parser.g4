parser grammar qasm3Parser;

options {
    tokenVocab = qasm3Lexer;
}

program: header (globalStatement | statement)*;
header: version? include* io*;
version: OPENQASM (Integer | RealNumber) SEMICOLON;
include: INCLUDE StringLiteral SEMICOLON;

ioIdentifier: INPUT | OUTPUT;
io: ioIdentifier classicalType Identifier SEMICOLON;

globalStatement
    : subroutineDefinition
    | externDeclaration
    | quantumGateDefinition
    | calibration
    | quantumDeclarationStatement  // qubits are declared globally
    | pragma
    ;

statement
    : expressionStatement
    | assignmentStatement
    | classicalDeclarationStatement
    | branchingStatement
    | loopStatement
    | endStatement
    | aliasStatement
    | quantumStatement
    ;

quantumDeclarationStatement : quantumDeclaration SEMICOLON ;
classicalDeclarationStatement: (classicalDeclaration | constantDeclaration) SEMICOLON;
classicalAssignment: Identifier designator? assignmentOperator expression;
assignmentStatement: (classicalAssignment | quantumMeasurementAssignment) SEMICOLON;
returnSignature: ARROW classicalType;

/*** Types and Casting ***/

designator: LBRACKET expression RBRACKET;
identifierList: Identifier (COMMA Identifier)*;

/** Quantum Types **/
quantumDeclaration: QREG Identifier designator? | QUBIT designator? Identifier;
quantumArgument: QREG Identifier designator? | QUBIT designator? Identifier;

/** Classical Types **/
bitType: BIT | CREG;
singleDesignatorType: INT | UINT | FLOAT | ANGLE;
noDesignatorType: BOOL | DURATION | STRETCH;

classicalType
    : singleDesignatorType designator
    | noDesignatorType
    | bitType designator?
    | COMPLEX LBRACKET numericType RBRACKET
    ;

// numeric OpenQASM types
numericType: singleDesignatorType designator;

constantDeclaration: CONST Identifier equalsExpression;

// if multiple variables declared at once, either none are assigned or all are assigned
// prevents ambiguity w/ qubit arguments in subroutine calls
singleDesignatorDeclaration: singleDesignatorType designator Identifier equalsExpression?;

noDesignatorDeclaration: noDesignatorType Identifier equalsExpression?;

bitDeclaration: ( CREG Identifier designator? | BIT designator? Identifier ) equalsExpression?;
complexDeclaration: COMPLEX LBRACKET numericType RBRACKET Identifier equalsExpression?;

classicalDeclaration
    : singleDesignatorDeclaration
    | noDesignatorDeclaration
    | bitDeclaration
    | complexDeclaration
    ;

classicalTypeList: classicalType (COMMA classicalType)*;
classicalArgument
    :
    (
        singleDesignatorType designator |
        noDesignatorType
    ) Identifier
    | CREG Identifier designator?
    | BIT designator? Identifier
    | COMPLEX LBRACKET numericType RBRACKET Identifier
    ;

classicalArgumentList: classicalArgument (COMMA classicalArgument)*;

anyTypeArgument: classicalArgument | quantumArgument;
anyTypeArgumentList: anyTypeArgument (COMMA anyTypeArgument)*;

/** Aliasing **/
aliasStatement: LET Identifier EQUALS indexIdentifier SEMICOLON;

/** Register Concatenation and Slicing **/

indexIdentifier
    : Identifier rangeDefinition
    | Identifier ( LBRACKET expressionList RBRACKET )?
    | indexIdentifier DOUBLE_PIPE indexIdentifier
    ;

indexIdentifierList
    : indexIdentifier ( COMMA indexIdentifier )*
    ;

rangeDefinition
    : LBRACKET expression? COLON expression? ( COLON expression )? RBRACKET
    ;

/*** Gates and Built-in Quantum Instructions ***/

quantumGateDefinition
    : GATE quantumGateSignature quantumBlock
    ;

quantumGateSignature
    : quantumGateName ( LPAREN identifierList? RPAREN )? identifierList
    ;

quantumGateName: U_ | CX | Identifier;
quantumBlock
    : LBRACE ( quantumStatement | quantumLoop )* RBRACE
    ;

// loops containing only quantum statements allowed in gates
quantumLoop
    : loopSignature quantumLoopBlock
    ;

quantumLoopBlock
    : quantumStatement
    | LBRACE quantumStatement* RBRACE
    ;

quantumStatement
    : quantumInstruction SEMICOLON
    | timingStatement
    ;

quantumInstruction
    : quantumGateCall
    | quantumPhase
    | quantumMeasurement
    | quantumReset
    | quantumBarrier
    ;

quantumPhase
    : quantumGateModifier* GPHASE LPAREN expression RPAREN indexIdentifierList?
    ;

quantumReset
    : RESET indexIdentifierList
    ;

quantumMeasurement
    : MEASURE indexIdentifier
    ;

quantumMeasurementAssignment
    : quantumMeasurement (ARROW indexIdentifier)?
    | indexIdentifier EQUALS quantumMeasurement
    ;

quantumBarrier
    : BARRIER indexIdentifierList?
    ;

quantumGateModifier
    : (INV | powModifier | ctrlModifier) AT
    ;

powModifier
    : POW LPAREN expression RPAREN
    ;

ctrlModifier
    : (CTRL | NEGCTRL) ( LPAREN expression RPAREN )?
    ;

quantumGateCall
    : quantumGateModifier* quantumGateName ( LPAREN expressionList RPAREN )? indexIdentifierList
    ;

/*** Classical Instructions ***/

unaryOperator: TILDE | EXCLAMATION_POINT | MINUS;

expressionStatement
    : expression SEMICOLON
    ;

expression
    // include terminator/unary as base cases to simplify parsing
    : expressionTerminator
    | unaryExpression
    // expression hierarchy
    | logicalAndExpression
    | expression DOUBLE_PIPE logicalAndExpression
    ;

/**  Expression hierarchy for non-terminators. Adapted from ANTLR4 C
  *  grammar: https://github.com/antlr/grammars-v4/blob/master/c/C.g4
  * Order (first to last evaluation):
    Terminator (including Parens),
    Unary Op,
    Multiplicative
    Additive
    Bit Shift
    Comparison
    Equality
    Bit And
    Exlusive Or (xOr)
    Bit Or
    Logical And
    Logical Or
**/

logicalAndExpression
    : bitOrExpression
    | logicalAndExpression DOUBLE_AMPERSAND bitOrExpression
    ;

bitOrExpression
    : xOrExpression
    | bitOrExpression PIPE xOrExpression
    ;

xOrExpression
    : bitAndExpression
    | xOrExpression CARET bitAndExpression
    ;

bitAndExpression
    : equalityExpression
    | bitAndExpression AMPERSAND equalityExpression
    ;

equalityExpression
    : comparisonExpression
    | equalityExpression EqualityOperator comparisonExpression
    ;

comparisonExpression
    : bitShiftExpression
    | comparisonExpression ComparisonOperator bitShiftExpression
    ;

bitShiftExpression
    : additiveExpression
    | bitShiftExpression BitshiftOperator additiveExpression
    ;

additiveExpression
    : multiplicativeExpression
    | additiveExpression (PLUS | MINUS) multiplicativeExpression
    ;

multiplicativeExpression
    // base case either terminator or unary
    : powerExpression
    | unaryExpression
    | multiplicativeExpression (ASTERISK | SLASH | PERCENT) ( powerExpression | unaryExpression )
    ;

unaryExpression
    : unaryOperator powerExpression
    ;

powerExpression
    : expressionTerminator
    | expressionTerminator DOUBLE_ASTERISK powerExpression
    ;

expressionTerminator
    : Constant
    | Integer
    | RealNumber
    | ImagNumber
    | BooleanLiteral
    | Identifier
    | StringLiteral
    | builtInCall
    | externOrSubroutineCall
    | timingIdentifier
    | LPAREN expression RPAREN
    | expressionTerminator LBRACKET expression RBRACKET
    ;
/** End expression hierarchy **/

builtInCall: (BuiltinMath | castOperator) LPAREN expressionList RPAREN;

castOperator: classicalType;

expressionList: expression (COMMA expression)*;

equalsExpression: EQUALS expression;
assignmentOperator : EQUALS | CompoundAssignmentOperator;

setDeclaration
    : LBRACE expressionList RBRACE
    | rangeDefinition
    | Identifier
    ;

programBlock
    : statement | controlDirective
    | LBRACE ( statement | controlDirective )* RBRACE
    ;

branchingStatement: IF LPAREN expression RPAREN programBlock (ELSE programBlock)?;

loopSignature
    : FOR Identifier IN setDeclaration
    | WHILE LPAREN expression RPAREN
    ;

loopStatement: loopSignature programBlock;
endStatement: END SEMICOLON;
returnStatement: RETURN (expression | quantumMeasurement)? SEMICOLON;

controlDirective
    : (BREAK| CONTINUE) SEMICOLON
    | endStatement
    | returnStatement
    ;

externDeclaration: EXTERN Identifier LPAREN classicalTypeList? RPAREN returnSignature? SEMICOLON;

// if have function call w/ out args, is ambiguous; may get matched as identifier
externOrSubroutineCall: Identifier LPAREN expressionList? RPAREN;

/*** Subroutines ***/
subroutineDefinition: DEF Identifier LPAREN anyTypeArgumentList? RPAREN returnSignature? subroutineBlock;
subroutineBlock: LBRACE statement* returnStatement? RBRACE;

/*** Directives ***/
pragma: PRAGMA LBRACE statement* RBRACE;

/*** Circuit Timing ***/
timingBox: BOX designator? quantumBlock;
timingIdentifier: TimingLiteral | DURATIONOF LPAREN (Identifier | quantumBlock) RPAREN;
timingInstruction: BuiltinTimingInstruction ( LPAREN expressionList? RPAREN )? designator indexIdentifierList;
timingStatement: timingInstruction SEMICOLON | timingBox;

/*** Pulse Level Descriptions of Gates and Measurement ***/
// TODO: Update when pulse grammar is formalized
calibration: calibrationGrammarDeclaration | calibrationDefinition;
calibrationGrammarDeclaration: DEFCALGRAMMAR StringLiteral SEMICOLON;
// For now, the defcal parser just matches anything at all within the braces.
calibrationDefinition: DEFCAL Identifier (LPAREN calibrationArgumentList? RPAREN)? identifierList returnSignature? LBRACE .*? RBRACE;
calibrationArgumentList: classicalArgumentList | expressionList;
