package it.uniroma1.diag.config;


import it.uniroma1.diag.exception.MissingPropertyException;
import lombok.extern.slf4j.Slf4j;

import java.util.Properties;

/**
 * Validator for Configuration
 *
 * @author Federico Maria Scafoglieri
 **/
@Slf4j
class ConfigurationValidator {

    public static boolean isValid(Properties properties){
        for(ConfigurationMandatoryProperty configurationMandatoryProperty : ConfigurationMandatoryProperty.values()){
            log.debug(configurationMandatoryProperty.name());
            if(!properties.containsKey(configurationMandatoryProperty.name()))
                throw new MissingPropertyException("Missing property " + configurationMandatoryProperty.name());
        }
        return true;
    }

}
