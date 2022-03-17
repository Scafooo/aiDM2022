package it.uniroma1.diag.formula;

public interface LogicalOperator extends Formula {

    Formula getDomain();

    Formula getRange();
}
