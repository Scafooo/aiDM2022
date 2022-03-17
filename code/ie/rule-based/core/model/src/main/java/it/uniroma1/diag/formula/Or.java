package it.uniroma1.diag.formula;

import lombok.Data;
import lombok.extern.slf4j.Slf4j;

import java.util.HashSet;

/**
 * This class represents the operator Or (Disjunction)
 *
 * @author Federico Maria Scafoglieri
 */
@Slf4j
@Data
public class Or implements LogicalOperator {

    /** Symbol for the disjunction in FOL */
    private Character symbolFOL = '∨';

    /** Symbol for the disjunction in Prolog */
    private String symbolProlog = "||";

    /** Formula in the first argument */
    private Formula domain;

    /** Formula in the second argument */
    private Formula range;

    /** Constructor for Or */
    public Or(Formula domain, Formula range) {
        this.domain = domain;
        this.range = range;
    }

    @Override
    public String toFOLSyntax() {
        return "( "
                + this.domain.toFOLSyntax()
                + " "
                + this.symbolFOL
                + " "
                + this.range.toFOLSyntax()
                + " )";
    }

    @Override
    public String toPrologSyntax() {
        return "( "
                + this.domain.toPrologSyntax()
                + " "
                + this.symbolProlog
                + " "
                + this.range.toPrologSyntax()
                + " )";
    }

}
