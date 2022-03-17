package it.uniroma1.diag.exception;

/**
 * @author Federico Maria Scafoglieri
 **/
public class MissingPropertyException extends InvalidConfigurationException {

    public MissingPropertyException(String message) {
        super(message);
    }
}
