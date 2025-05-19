import { useState } from 'react'
import univLogo from './assets/logo.png'
import './App.css'
import './index.css'
import { TextareaWithButton } from './MessageForm'

function App() {

  return (
    <>
      <div className='item-center flex justify-center'>
        
        <a href="https://hamzanwadi.ac.id" target="_blank">
          <img src={univLogo} className="h-20" alt="Hamzanwadi logo" />
        </a>
      </div>
      <TextareaWithButton />
    </>
  )
}

export default App
