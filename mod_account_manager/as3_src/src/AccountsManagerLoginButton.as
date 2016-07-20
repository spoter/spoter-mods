package
{
	import net.wg.infrastructure.base.AbstractView;
	import flash.events.*;
	import flash.display.*;
	import flash.utils.*;
	import components.AMButton;
	import net.wg.gui.login.impl.views.SimpleForm;
	import net.wg.gui.login.impl.LoginPage;

	public class AccountsManagerLoginButton extends AbstractView 
	{
		public var py_log: Function;
		public var py_openAccMngr: Function;
		public var py_getTranslate: Function;

		private var isLobby: Boolean = false;
		private var amBtn: AMButton;

		private var _login: LoginPage;
		private var _form: SimpleForm;

		public function AccountsManagerLoginButton() 
		{
			super();
		}

		public function as_populateLogin(): void {
			try {
				this.isLobby = false;
				this._login = this.recursiveFindDOC(DisplayObjectContainer(stage), "LoginPageUI") as LoginPage;
				this._form = this.recursiveFindDOC(DisplayObjectContainer(stage), "LoginFormUI") as SimpleForm;

				if (this._login != null) {
					this.amBtn = new AMButton();
					this.amBtn.tooltip = this.py_getTranslate().tooltip_l10n;
					this._login.addChild(this.amBtn);
					this.addEventListener(Event.RESIZE, this.resize);
					this.amBtn.addEventListener(TextEvent.LINK, this.handleAMButtonClick);
					this.resize();
				}
			} catch(err: Error) {
				this.py_log(err.getStackTrace());
			}
		}

		public function as_populateLobby(): void {
			try {
				this.isLobby = true;
			} catch(err: Error) {
				this.py_log(err.getStackTrace());
			}
		}

		private function resize(e : Event = null) : void
		{
			if (!this.isLobby) {
				this.amBtn.x = this._form.parent.x + this._form.keyboardLang.x;
				this.amBtn.y = this._form.parent.y + this._form.submit.y;
			}
		}

		private function handleAMButtonClick(e : TextEvent) : void
		{
			this.py_openAccMngr();
		}

		override protected function onPopulate() : void {
			super.onPopulate();
			//App.instance.loaderMgr.loadLibraries(Vector.<String>(["controls.swf"]));
		}

		private function recursiveFindDOC(dOC:DisplayObjectContainer, className:String) : DisplayObjectContainer {
			var child:DisplayObject = null;
			var childOC:DisplayObjectContainer = null;
			var i:int = 0;
			var result:DisplayObjectContainer = null;
			while (i < dOC.numChildren) {
				child = dOC.getChildAt(i);
				if ((child is DisplayObject) && (getQualifiedClassName(child) == className)) result = child as DisplayObjectContainer;
				if (result != null) return result;
				childOC = child as DisplayObjectContainer;
				if ((childOC) && (childOC.numChildren > 0)) result = this.recursiveFindDOC(childOC, className);
				i++;
			}
			return result;
		}

	}

}
