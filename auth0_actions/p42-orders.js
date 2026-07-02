/**
* Handler that will be called during the execution of a PostLogin flow.
*
* @param {Event} event - Details about the user and the context in which they are logging in.
* @param {PostLoginAPI} api - Interface whose methods can be used to change the behavior of the login.
*/
exports.onExecutePostLogin = async (event, api) => {
  if(event.client.client_id == 'hqvoam0pzpABmubbw2Hgq026cjctsfqP'){ // Client ID of Pizza42
    let orders = [];
    console.log('orders', event.user.app_metadata['pizza42/orders']);
    if(event.user.app_metadata['pizza42/orders']){
      api.idToken.setCustomClaim('pizza42/orders', event.user.app_metadata['pizza42/orders'])
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
// exports.onContinuePostLogin = async (event, api) => {
// };

