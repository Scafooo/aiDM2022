package it.uniroma1.diag.formula;

import org.junit.Test;
import java.util.Collection;
import java.util.LinkedList;

public class FormulaTest {

    @Test
    public void shouldAnswerWithTrue() {

        Collection<Term> collection = new LinkedList<>();
        collection.add(new Variable("x"));
        collection.add(new Variable("y"));
        collection.add(new Constant("\'c\'"));

        Formula formula0 = new Predicate("Test", collection);

        Formula formula1 = new And(formula0, formula0);
        Formula formula2 = new Or(formula1, formula0);
        Formula formula3 = new Implication(formula2, new Negation(formula0));
        System.out.println(formula3.toFOLSyntax());
        System.out.println(formula3.toFOLSyntax());
        System.out.println(formula3.toPrologSyntax());

    }
}
