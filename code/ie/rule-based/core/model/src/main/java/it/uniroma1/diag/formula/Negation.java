package it.uniroma1.diag.formula;

import it.uniroma1.diag.formula.Formula;
import lombok.Data;
import lombok.extern.slf4j.Slf4j;

import java.util.Collection;
import java.util.HashSet;
import java.util.LinkedList;

/**
 * This class represents the operator Negation
 *
 * @author Federico Maria Scafoglieri
 */
@Slf4j
@Data
public class Negation implements Formula {

    /** Symbol for the negation in FOL */
    private Character symbolFOL = '¬';

    /** Symbol for the negation in Prolog*/
    private String symbolProlog = "\\+";

    /** Formula in the first argument */
    private Formula formula;

    /** Constructor for Negation */
    public Negation(Formula formula) {
        this.formula = formula;
    }

    @Override
    public String toFOLSyntax() {
        return this.symbolFOL + this.formula.toFOLSyntax();
    }

    @Override
    public String toPrologSyntax() {
        return this.symbolProlog + this.formula.toPrologSyntax();
    }

}
