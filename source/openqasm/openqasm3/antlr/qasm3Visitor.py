# Generated from qasm3.g4 by ANTLR 4.9.3
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .qasm3Parser import qasm3Parser
else:
    from qasm3Parser import qasm3Parser

# This class defines a complete generic visitor for a parse tree produced by qasm3Parser.

class qasm3Visitor(ParseTreeVisitor):

    # Visit a parse tree produced by qasm3Parser#program.
    def visitProgram(self, ctx:qasm3Parser.ProgramContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#header.
    def visitHeader(self, ctx:qasm3Parser.HeaderContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#version.
    def visitVersion(self, ctx:qasm3Parser.VersionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#include.
    def visitInclude(self, ctx:qasm3Parser.IncludeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#ioIdentifier.
    def visitIoIdentifier(self, ctx:qasm3Parser.IoIdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#io.
    def visitIo(self, ctx:qasm3Parser.IoContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#globalStatement.
    def visitGlobalStatement(self, ctx:qasm3Parser.GlobalStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#statement.
    def visitStatement(self, ctx:qasm3Parser.StatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#quantumDeclarationStatement.
    def visitQuantumDeclarationStatement(self, ctx:qasm3Parser.QuantumDeclarationStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#classicalDeclarationStatement.
    def visitClassicalDeclarationStatement(self, ctx:qasm3Parser.ClassicalDeclarationStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#classicalAssignment.
    def visitClassicalAssignment(self, ctx:qasm3Parser.ClassicalAssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#assignmentStatement.
    def visitAssignmentStatement(self, ctx:qasm3Parser.AssignmentStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#returnSignature.
    def visitReturnSignature(self, ctx:qasm3Parser.ReturnSignatureContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#designator.
    def visitDesignator(self, ctx:qasm3Parser.DesignatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#identifierList.
    def visitIdentifierList(self, ctx:qasm3Parser.IdentifierListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#quantumDeclaration.
    def visitQuantumDeclaration(self, ctx:qasm3Parser.QuantumDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#quantumArgument.
    def visitQuantumArgument(self, ctx:qasm3Parser.QuantumArgumentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#quantumArgumentList.
    def visitQuantumArgumentList(self, ctx:qasm3Parser.QuantumArgumentListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#bitType.
    def visitBitType(self, ctx:qasm3Parser.BitTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#singleDesignatorType.
    def visitSingleDesignatorType(self, ctx:qasm3Parser.SingleDesignatorTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#noDesignatorType.
    def visitNoDesignatorType(self, ctx:qasm3Parser.NoDesignatorTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#classicalType.
    def visitClassicalType(self, ctx:qasm3Parser.ClassicalTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#numericType.
    def visitNumericType(self, ctx:qasm3Parser.NumericTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#constantDeclaration.
    def visitConstantDeclaration(self, ctx:qasm3Parser.ConstantDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#singleDesignatorDeclaration.
    def visitSingleDesignatorDeclaration(self, ctx:qasm3Parser.SingleDesignatorDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#noDesignatorDeclaration.
    def visitNoDesignatorDeclaration(self, ctx:qasm3Parser.NoDesignatorDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#bitDeclaration.
    def visitBitDeclaration(self, ctx:qasm3Parser.BitDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#complexDeclaration.
    def visitComplexDeclaration(self, ctx:qasm3Parser.ComplexDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#classicalDeclaration.
    def visitClassicalDeclaration(self, ctx:qasm3Parser.ClassicalDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#classicalTypeList.
    def visitClassicalTypeList(self, ctx:qasm3Parser.ClassicalTypeListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#classicalArgument.
    def visitClassicalArgument(self, ctx:qasm3Parser.ClassicalArgumentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#classicalArgumentList.
    def visitClassicalArgumentList(self, ctx:qasm3Parser.ClassicalArgumentListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#anyTypeArgument.
    def visitAnyTypeArgument(self, ctx:qasm3Parser.AnyTypeArgumentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#anyTypeArgumentList.
    def visitAnyTypeArgumentList(self, ctx:qasm3Parser.AnyTypeArgumentListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#aliasStatement.
    def visitAliasStatement(self, ctx:qasm3Parser.AliasStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#indexIdentifier.
    def visitIndexIdentifier(self, ctx:qasm3Parser.IndexIdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#indexIdentifierList.
    def visitIndexIdentifierList(self, ctx:qasm3Parser.IndexIdentifierListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#rangeDefinition.
    def visitRangeDefinition(self, ctx:qasm3Parser.RangeDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#quantumGateDefinition.
    def visitQuantumGateDefinition(self, ctx:qasm3Parser.QuantumGateDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#quantumGateSignature.
    def visitQuantumGateSignature(self, ctx:qasm3Parser.QuantumGateSignatureContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#quantumGateName.
    def visitQuantumGateName(self, ctx:qasm3Parser.QuantumGateNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#quantumBlock.
    def visitQuantumBlock(self, ctx:qasm3Parser.QuantumBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#quantumLoop.
    def visitQuantumLoop(self, ctx:qasm3Parser.QuantumLoopContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#quantumLoopBlock.
    def visitQuantumLoopBlock(self, ctx:qasm3Parser.QuantumLoopBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#quantumStatement.
    def visitQuantumStatement(self, ctx:qasm3Parser.QuantumStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#quantumInstruction.
    def visitQuantumInstruction(self, ctx:qasm3Parser.QuantumInstructionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#quantumPhase.
    def visitQuantumPhase(self, ctx:qasm3Parser.QuantumPhaseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#quantumReset.
    def visitQuantumReset(self, ctx:qasm3Parser.QuantumResetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#quantumMeasurement.
    def visitQuantumMeasurement(self, ctx:qasm3Parser.QuantumMeasurementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#quantumMeasurementAssignment.
    def visitQuantumMeasurementAssignment(self, ctx:qasm3Parser.QuantumMeasurementAssignmentContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#quantumBarrier.
    def visitQuantumBarrier(self, ctx:qasm3Parser.QuantumBarrierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#quantumGateModifier.
    def visitQuantumGateModifier(self, ctx:qasm3Parser.QuantumGateModifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#powModifier.
    def visitPowModifier(self, ctx:qasm3Parser.PowModifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#ctrlModifier.
    def visitCtrlModifier(self, ctx:qasm3Parser.CtrlModifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#quantumGateCall.
    def visitQuantumGateCall(self, ctx:qasm3Parser.QuantumGateCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#unaryOperator.
    def visitUnaryOperator(self, ctx:qasm3Parser.UnaryOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#comparisonOperator.
    def visitComparisonOperator(self, ctx:qasm3Parser.ComparisonOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#equalityOperator.
    def visitEqualityOperator(self, ctx:qasm3Parser.EqualityOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#logicalOperator.
    def visitLogicalOperator(self, ctx:qasm3Parser.LogicalOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#expressionStatement.
    def visitExpressionStatement(self, ctx:qasm3Parser.ExpressionStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#expression.
    def visitExpression(self, ctx:qasm3Parser.ExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#logicalAndExpression.
    def visitLogicalAndExpression(self, ctx:qasm3Parser.LogicalAndExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#bitOrExpression.
    def visitBitOrExpression(self, ctx:qasm3Parser.BitOrExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#xOrExpression.
    def visitXOrExpression(self, ctx:qasm3Parser.XOrExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#bitAndExpression.
    def visitBitAndExpression(self, ctx:qasm3Parser.BitAndExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#equalityExpression.
    def visitEqualityExpression(self, ctx:qasm3Parser.EqualityExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#comparisonExpression.
    def visitComparisonExpression(self, ctx:qasm3Parser.ComparisonExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#bitShiftExpression.
    def visitBitShiftExpression(self, ctx:qasm3Parser.BitShiftExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#additiveExpression.
    def visitAdditiveExpression(self, ctx:qasm3Parser.AdditiveExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#multiplicativeExpression.
    def visitMultiplicativeExpression(self, ctx:qasm3Parser.MultiplicativeExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#unaryExpression.
    def visitUnaryExpression(self, ctx:qasm3Parser.UnaryExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#powerExpression.
    def visitPowerExpression(self, ctx:qasm3Parser.PowerExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#expressionTerminator.
    def visitExpressionTerminator(self, ctx:qasm3Parser.ExpressionTerminatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#booleanLiteral.
    def visitBooleanLiteral(self, ctx:qasm3Parser.BooleanLiteralContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#builtInCall.
    def visitBuiltInCall(self, ctx:qasm3Parser.BuiltInCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#builtInMath.
    def visitBuiltInMath(self, ctx:qasm3Parser.BuiltInMathContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#castOperator.
    def visitCastOperator(self, ctx:qasm3Parser.CastOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#expressionList.
    def visitExpressionList(self, ctx:qasm3Parser.ExpressionListContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#equalsExpression.
    def visitEqualsExpression(self, ctx:qasm3Parser.EqualsExpressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#assignmentOperator.
    def visitAssignmentOperator(self, ctx:qasm3Parser.AssignmentOperatorContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#discreteSet.
    def visitDiscreteSet(self, ctx:qasm3Parser.DiscreteSetContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#setDeclaration.
    def visitSetDeclaration(self, ctx:qasm3Parser.SetDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#programBlock.
    def visitProgramBlock(self, ctx:qasm3Parser.ProgramBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#branchingStatement.
    def visitBranchingStatement(self, ctx:qasm3Parser.BranchingStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#loopSignature.
    def visitLoopSignature(self, ctx:qasm3Parser.LoopSignatureContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#loopStatement.
    def visitLoopStatement(self, ctx:qasm3Parser.LoopStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#endStatement.
    def visitEndStatement(self, ctx:qasm3Parser.EndStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#returnStatement.
    def visitReturnStatement(self, ctx:qasm3Parser.ReturnStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#controlDirective.
    def visitControlDirective(self, ctx:qasm3Parser.ControlDirectiveContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#externDeclaration.
    def visitExternDeclaration(self, ctx:qasm3Parser.ExternDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#externOrSubroutineCall.
    def visitExternOrSubroutineCall(self, ctx:qasm3Parser.ExternOrSubroutineCallContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#subroutineDefinition.
    def visitSubroutineDefinition(self, ctx:qasm3Parser.SubroutineDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#subroutineBlock.
    def visitSubroutineBlock(self, ctx:qasm3Parser.SubroutineBlockContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#pragma.
    def visitPragma(self, ctx:qasm3Parser.PragmaContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#timingType.
    def visitTimingType(self, ctx:qasm3Parser.TimingTypeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#timingBox.
    def visitTimingBox(self, ctx:qasm3Parser.TimingBoxContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#timingIdentifier.
    def visitTimingIdentifier(self, ctx:qasm3Parser.TimingIdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#timingInstructionName.
    def visitTimingInstructionName(self, ctx:qasm3Parser.TimingInstructionNameContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#timingInstruction.
    def visitTimingInstruction(self, ctx:qasm3Parser.TimingInstructionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#timingStatement.
    def visitTimingStatement(self, ctx:qasm3Parser.TimingStatementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#calibration.
    def visitCalibration(self, ctx:qasm3Parser.CalibrationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#calibrationGrammarDeclaration.
    def visitCalibrationGrammarDeclaration(self, ctx:qasm3Parser.CalibrationGrammarDeclarationContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#calibrationDefinition.
    def visitCalibrationDefinition(self, ctx:qasm3Parser.CalibrationDefinitionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#calibrationGrammar.
    def visitCalibrationGrammar(self, ctx:qasm3Parser.CalibrationGrammarContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by qasm3Parser#calibrationArgumentList.
    def visitCalibrationArgumentList(self, ctx:qasm3Parser.CalibrationArgumentListContext):
        return self.visitChildren(ctx)



del qasm3Parser