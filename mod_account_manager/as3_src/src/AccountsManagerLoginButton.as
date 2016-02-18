package
{
	import net.wg.infrastructure.base.AbstractView;
	import net.wg.gui.login.impl.LoginPage;
	import flash.display.MovieClip;
	import flash.events.Event;
	import flash.events.TextEvent;
	import net.wg.gui.login.impl.views.SimpleForm;
	import net.wg.infrastructure.events.LoaderEvent;
	import net.wg.infrastructure.interfaces.IView;
	import net.wg.gui.login.impl.ev.LoginViewStackEvent;
	import components.AMButton;

	public class AccountsManagerLoginButton extends AbstractView 
	{
		public var py_log			: Function;
		public var py_openAccMngr	: Function;
		public var py_getTranslate	: Function;

		private var _login	: LoginPage;
		private var _form	: SimpleForm;
		
		private var amBtn	: AMButton;

		public function AccountsManagerLoginButton() 
		{
			super();
			this.init();
		}

		override protected function nextFrameAfterPopulateHandler() : void
		{
			if(this.parent != App.instance)
			{
				(App.instance as MovieClip).addChild(this);
			}
		}

		private function onViewLoaded(e : LoaderEvent) : void
		{
			this.processView(e.view, false);
		}

		private function onViewChanged(e : LoginViewStackEvent) : void
		{
			setupForm(e.view as SimpleForm);
		}

		private function processView(view : IView, populated : Boolean) : void
		{
			var alias:String = view.as_alias;
			try
			{
				if (alias == "login")
				{
					this._login = view as LoginPage;
					this._login.loginViewStack.addEventListener(LoginViewStackEvent.VIEW_CHANGED, this.onViewChanged);
					this.amBtn = new AMButton();
					this.amBtn.tooltip = this.py_getTranslate().tooltip_l10n;
					this._login.addChild(this.amBtn);
					this.addEventListener(Event.RESIZE, this.resize);
					this.amBtn.addEventListener(TextEvent.LINK, this.handleAMButtonClick);
				}
			} catch(err : Error)
			{
				this.py_log("processView " + err.message);
			}
		}

		private function resize(e : Event): void
		{
			this.setButtonPosition();
		}

		private function setButtonPosition(): void
		{
			if (this._form != null && this._form.submit != null && this._form.keyboardLang != null)
			{
				this.amBtn.x = this._form.parent.x + this._form.keyboardLang.x;
				this.amBtn.y = this._form.parent.y + this._form.submit.y;
			}
		}

		private function handleAMButtonClick(e : TextEvent) : void
		{
			this.py_openAccMngr();
		}

		private function init(e : Event = null) : void
		{
			if(!this.stage)
			{
				this.addEventListener(Event.ADDED_TO_STAGE, this.init);
				return;
			}
			this.removeEventListener(Event.ADDED_TO_STAGE, this.init);
			App.containerMgr.loader.addEventListener(LoaderEvent.VIEW_LOADED, this.onViewLoaded);
		}

		private function setupForm(form : SimpleForm) : void
		{
            if (form != null && form.login != null && form.pass != null)
			{
				this._form = form;
				this.setButtonPosition();
			}
        }

	}

}
