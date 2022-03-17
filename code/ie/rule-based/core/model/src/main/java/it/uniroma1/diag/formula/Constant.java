package it.uniroma1.diag.formula;

import lombok.Data;
import lombok.extern.slf4j.Slf4j;

/**
 * This class represents a Constant
 *
 * @author Federico Maria Scafoglieri
 */
@Slf4j
@Data
public class Constant implements Term {

    /** The name of the Constant */
    private String name;

    /**
     * Constructor for Constant. TODO
     *
     * @param name the name of Constant
     */
    public Constant(String name) {
        if (!name.startsWith("\'") || !name.endsWith("\'")) {
            throw new InvalidConstantException("Constants need to be inside double quote \' \'");
        }
        this.name = name;
    }
}
