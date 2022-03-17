package it.uniroma1.diag.formula;

import lombok.Data;
import lombok.extern.slf4j.Slf4j;

/**
 * This class represents a Variable
 *
 * @author Federico Maria Scafoglieri
 */
@Slf4j
@Data
public class Variable implements Term {

    /** The name of the Variable */
    private String name;

    /**
     * Constructor for Variable. TODO
     *
     * @param name the name of Variable
     */
    public Variable(String name) {
        this.name = name;
    }
}
