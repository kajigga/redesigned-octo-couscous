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
      console.log('requested scopes: ', requestedScopes);
      api.accessToken.removeScope('pizza42-order');
      if (!!event.user.email_verified) {
        console.log('user email not verified, doing that now');
        // We render the form here so they can verify their email address
        api.prompt.render('ap_nyXekNRzqQHXDRBd9Zgo3L'); // this is the first to validate a user's email address
        
      }else{
        console.log('user email verified, adding scope');
        api.accessToken.addScope('pizza42-order');
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
    if (event.user.email_verified) {
      console.log('user email verified from form, add scope');
      api.accessToken.addScope('pizza42-order');
    }
   
  }
};

