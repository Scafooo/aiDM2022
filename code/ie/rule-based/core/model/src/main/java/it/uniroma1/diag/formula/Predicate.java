package it.uniroma1.diag.formula;

import lombok.Data;
import lombok.NonNull;
import lombok.extern.slf4j.Slf4j;

import java.util.Collection;
import java.util.LinkedList;

/**
 * This class represents an Atom
 *
 * @author Federico Maria Scafoglieri
 */
@Slf4j
@Data
public class Predicate implements Formula {

    /** Name of the predicate for example the name of Atom(x, y) is Atom */
    String name;

    /** The ordered set of terms appearing in the Atom */
    Collection<Term> terms;

    /**
     * Constructor for Atom. TODO
     *
     * @param name the name of Atom
     */
    public Predicate(@NonNull String name) {
        this.name = name;
        this.terms = new LinkedList<>();
    }

    /**
     * Constructor for Atom. TODO
     *
     * @param predicateName the name of Atom
     */
    public Predicate(@NonNull String predicateName,@NonNull Collection<Term> collection) {
        this.name = predicateName;
        this.terms = collection;
    }

    /**
     * Add a new Term to the Atom. For example give the Atom(x, y) calling add(z) we obtain Atom(x, y, z)
     *
     * @param term
     */
    public void add(Term term){
        this.terms.add(term);
    }

    /**
     * FolSyntax for the Atom ex. Atom(x,y,z)
     *
     * @return the String of the Atom in FOL syntax
     */
    @Override
    public String toFOLSyntax(){
        StringBuilder stringBuilder = new StringBuilder();
        for(Term term: this.terms){
             stringBuilder.append(term.getName()).append(",");
        }
        return this.name + "("
                + stringBuilder.toString().substring(0, stringBuilder.toString().length()-1)
                + ")";
    }

    @Override
    public String toPrologSyntax() {
        return this.toFOLSyntax();
    }

}
