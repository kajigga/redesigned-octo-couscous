/**
* Handler that will be called during the execution of a PostLogin flow.
*
* @param {Event} event - Details about the user and the context in which they are logging in.
* @param {PostLoginAPI} api - Interface whose methods can be used to change the behavior of the login.
*/
exports.onExecutePostLogin = async (event, api) => {
  // if intent == 'order' and event.user.app_m
  
  if(event.client.client_id == 'hqvoam0pzpABmubbw2Hgq026cjctsfqP'){ // Pizza42
    console.log('this is pizza42 client');
    
    const requestedScopes = event.transaction?.requested_scopes || [];
    
    if(requestedScopes.includes('pizza42-order')){
      api.prompt.render('ap_cyPdra5WkNT7ufMiEQPoGX'); // this is the first to collect a user's address
    }else{  
      if (event.user.user_metadata?.address_street){
        api.idToken.setCustomClaim('pizza42/address_street', event.user.user_metadata.address_street);
        api.idToken.setCustomClaim('pizza42/address_city', event.user.user_metadata.address_city);
        api.idToken.setCustomClaim('pizza42/address_zip', event.user.user_metadata.address_zip);
      }
    }
  
  }
  
};


/**
* Handler that will be invoked when this action is resuming after an external redirect. If your
* onExecutePostLogin function does not perform a redirect, this function can be safely ignored.
*
* @param {Event} event - Details about the user and the context in which they are logging in.
* @param {PostLoginAPI} api - Interface whose methods can be used to change the behavior of the login.
*/
exports.onContinuePostLogin = async (event, api) => {
  if(event.client.client_id == 'hqvoam0pzpABmubbw2Hgq026cjctsfqP'){ // Pizza42
    console.log('user md', event.user.user_metadata);
    api.idToken.setCustomClaim('pizza42/address_street', event.user.user_metadata.address_street);
    api.idToken.setCustomClaim('pizza42/address_city', event.user.user_metadata.address_city);
    api.idToken.setCustomClaim('pizza42/address_zip', event.user.user_metadata.address_zip);
   
  }
};

