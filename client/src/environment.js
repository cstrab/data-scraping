function readEnv(variables) {
    const environment = {};
    variables.forEach(variable => {
        environment[variable] = process.env.NODE_ENV === 'production' ? window.env[variable] : process.env[variable];
    });
    return environment
}

export const environment = readEnv([
    'REACT_APP_API_URL',
])