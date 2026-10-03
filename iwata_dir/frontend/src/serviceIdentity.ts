/** Identity is the service's persistent state UUID, never a path or credential. */
let current:string|null=null;
export function serviceIdentity(){return current;}
export function setServiceIdentity(value:string|null){
 if(value!==null&&(typeof value!=='string'||!value))throw Error('保存先の識別を読めません。新しい要求の送信を止めています。');
 current=value;
}
export function requireServiceIdentity(){
 if(!current)throw Error('保存先の識別をまだ確認できません。状態を再確認してから送信してください。保存済み結果の読取りは続けられます。');
 return current;
}
