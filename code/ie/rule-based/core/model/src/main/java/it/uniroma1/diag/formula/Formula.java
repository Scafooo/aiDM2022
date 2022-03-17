package it.uniroma1.diag.formula;

import java.util.HashSet;

public interface Formula {

    String toFOLSyntax();

    String toPrologSyntax();
}
